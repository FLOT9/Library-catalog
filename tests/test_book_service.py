from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.library_catalog.api.v1.schemas.book import BookCreate, ShowBook
from src.library_catalog.data.models.book import Book
from src.library_catalog.domain.services.book_service import BookService


class FakeBookRepository:
    def __init__(self, created_book: Book) -> None:
        self.created_book = created_book
        self.created_data = None

    async def find_by_isbn(self, isbn) -> None:
        return None

    async def create(self, **kwargs) -> Book:
        self.created_data = kwargs
        return self.created_book


class FakeOpenLibraryClient:
    async def enrich(self, **kwargs) -> dict:
        return {"rating": 4.4}


@pytest.mark.asyncio
async def test_create_book_returns_show_book():
    now = datetime.now(UTC)
    saved_book = Book(
        book_id=uuid4(),
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
    repository = FakeBookRepository(saved_book)
    service = BookService(repository, FakeOpenLibraryClient())
    book_data = BookCreate(
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
        isbn="9780132350884",
        description="A handbook of agile software craftsmanship.",
    )
    result = await service.create_book(book_data)
    assert isinstance(result, ShowBook)
    assert repository.created_data is not None
    assert repository.created_data["title"] == book_data.title
    assert repository.created_data["isbn"] == book_data.isbn
    assert repository.created_data["extra"] == {"rating": 4.4}


