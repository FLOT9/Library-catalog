from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.library_catalog.api.v1.dependencies import get_book_service
from src.library_catalog.api.v1.schemas.book import BookCreate, ShowBook
from src.library_catalog.domain.exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
)
from src.library_catalog.main import app


class FakeBookService:
    def __init__(
        self,
        book: ShowBook | None = None,
        error: Exception | None = None,
    ) -> None:
        self.book = book
        self.error = error

    async def create_book(self, book_data: BookCreate) -> ShowBook:
        if self.error is not None:
            raise self.error
        assert self.book is not None
        return self.book

    async def get_book(self, book_id: UUID) -> ShowBook:
        if self.error is not None:
            raise self.error
        assert self.book is not None
        return self.book


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()


def make_show_book(book_id: UUID | None = None) -> ShowBook:
    now = datetime.now(UTC)
    return ShowBook(
        book_id=book_id or uuid4(),
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
        available=True,
        isbn="9780132350884",
        description="A handbook of agile software craftsmanship.",
        extra=None,
        created_at=now,
        updated_at=now,
    )


def create_payload() -> dict:
    return {
        "title": "Clean Code",
        "author": "Robert Martin",
        "year": 2008,
        "genre": "Programming",
        "pages": 464,
        "isbn": "9780132350884",
        "description": "A handbook of agile software craftsmanship.",
    }


@pytest.mark.asyncio
async def test_create_book_returns_201():
    book = make_show_book()
    app.dependency_overrides[get_book_service] = lambda: FakeBookService(book=book)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/books", json=create_payload())

    assert response.status_code == 201
    assert response.json()["book_id"] == str(book.book_id)
    assert response.json()["title"] == "Clean Code"


@pytest.mark.asyncio
async def test_get_book_returns_404_when_book_not_found():
    book_id = uuid4()
    service = FakeBookService(error=BookNotFoundException(book_id))
    app.dependency_overrides[get_book_service] = lambda: service
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/books/{book_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Book with id {book_id} not found"}


@pytest.mark.asyncio
async def test_create_book_returns_409_for_duplicate_isbn():
    isbn = "9780132350884"
    service = FakeBookService(error=BookAlreadyExistsException(isbn))
    app.dependency_overrides[get_book_service] = lambda: service
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/books", json=create_payload())

    assert response.status_code == 409
    assert response.json() == {"detail": f"Book with ISBN '{isbn}' already exists"}


@pytest.mark.asyncio
async def test_cors_allows_browser_preflight_request():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/api/v1/books",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ("http://localhost:3000")
