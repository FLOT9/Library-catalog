from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.library_catalog.api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from src.library_catalog.data.models.book import Book
from src.library_catalog.domain.exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
)
from src.library_catalog.domain.services.book_service import BookService


class FakeBookRepository:
    def __init__(self, created_book: Book | None) -> None:
        self.created_book = created_book
        self.created_data = None
        self.isbn_book: Book | None = None
        self.delete_result = True
        self.deleted_book_id = None
        self.search_filters = None
        self.count_filters = None

    async def find_by_isbn(self, isbn) -> Book | None:
        return self.isbn_book

    async def get_by_id(self, book_id) -> Book | None:
        return self.created_book

    async def create(self, **kwargs) -> Book:
        self.created_data = kwargs
        assert self.created_book is not None
        return self.created_book

    async def delete(self, book_id) -> bool:
        self.deleted_book_id = book_id
        return self.delete_result

    async def find_by_filters(self, **kwargs) -> list[Book]:
        self.search_filters = kwargs
        return [self.created_book] if self.created_book is not None else []

    async def count_by_filters(self, **kwargs) -> int:
        self.count_filters = kwargs
        return 1 if self.created_book is not None else 0


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


@pytest.mark.asyncio
async def test_update_book_rejects_isbn_used_by_another_book():
    now = datetime.now(UTC)
    book_id = uuid4()
    existing_book = Book(
        book_id=book_id,
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
    conflicting_book = Book(
        book_id=uuid4(),
        title="Domain-Driven Design",
        author="Eric Evans",
        year=2003,
        genre="Programming",
        pages=560,
        available=True,
        isbn="9780321125217",
        description="Tackling complexity in software.",
        extra=None,
        created_at=now,
        updated_at=now,
    )
    repository = FakeBookRepository(existing_book)
    repository.isbn_book = conflicting_book
    service = BookService(repository, FakeOpenLibraryClient())

    with pytest.raises(BookAlreadyExistsException):
        await service.update_book(
            book_id,
            BookUpdate(isbn="978-0-321-12521-7"),
        )


@pytest.mark.asyncio
async def test_delete_book_deletes_existing_book():
    book_id = uuid4()
    repository = FakeBookRepository(None)
    service = BookService(repository, FakeOpenLibraryClient())

    result = await service.delete_book(book_id)

    assert result is None
    assert repository.deleted_book_id == book_id


@pytest.mark.asyncio
async def test_delete_book_raises_when_book_not_found():
    book_id = uuid4()
    repository = FakeBookRepository(None)
    repository.delete_result = False
    service = BookService(repository, FakeOpenLibraryClient())

    with pytest.raises(BookNotFoundException):
        await service.delete_book(book_id)

    assert repository.deleted_book_id == book_id


@pytest.mark.asyncio
async def test_search_books_passes_filters_and_pagination():
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

    books, total = await service.search_books(
        title="Clean",
        author="Martin",
        genre="Programming",
        year=2008,
        available=True,
        limit=10,
        offset=20,
    )

    assert len(books) == 1
    assert isinstance(books[0], ShowBook)
    assert books[0].book_id == saved_book.book_id
    assert total == 1
    assert repository.search_filters == {
        "title": "Clean",
        "author": "Martin",
        "genre": "Programming",
        "year": 2008,
        "limit": 10,
        "offset": 20,
        "available": True,
    }
    assert repository.count_filters == {
        "title": "Clean",
        "author": "Martin",
        "genre": "Programming",
        "year": 2008,
        "available": True,
    }
