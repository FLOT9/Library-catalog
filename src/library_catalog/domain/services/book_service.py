from datetime import UTC, datetime
from uuid import UUID

from ...api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from ...data.repositories.book_repository import BookRepository
from ...external.openlibrary.client import OpenLibraryClient
from ..exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    InvalidPagesException,
    InvalidYearException,
    OpenLibraryException,
    OpenLibraryTimeoutException,
)
from ..mappers.book_mapper import BookMapper


class BookService:
    def __init__(
        self,
        repository: BookRepository,
        openlibrary_client: OpenLibraryClient,
    ) -> None:
        self.book_repo = repository
        self.ol_client = openlibrary_client

    async def get_book(self, book_id: UUID) -> ShowBook:
        book = await self.book_repo.get_by_id(book_id)

        if book is None:
            raise BookNotFoundException(book_id)

        return BookMapper.to_show_book(book)

    async def create_book(self, book: BookCreate) -> ShowBook:
        if book.year < 1000 or book.year > datetime.now(UTC).year:
            raise InvalidYearException(book.year)
        if book.pages < 1:
            raise InvalidPagesException(book.pages)
        if book.isbn and await self.book_repo.find_by_isbn(book.isbn):
            raise BookAlreadyExistsException(book.isbn)
        extra = await self._enrich_book_data(book)

        data = book.model_dump()
        data["extra"] = extra

        saved_book = await self.book_repo.create(**data)

        return BookMapper.to_show_book(saved_book)

    async def _enrich_book_data(self, book: BookCreate) -> dict | None:
        try:
            return await self.ol_client.enrich(
                title=book.title,
                author=book.author,
                isbn=book.isbn,
            )
        except (OpenLibraryException, OpenLibraryTimeoutException):
            return None

    async def update_book(self, book_id: UUID, book_data: BookUpdate) -> ShowBook:
        existing_book = await self.book_repo.get_by_id(book_id)

        if existing_book is None:
            raise BookNotFoundException(book_id)

        if book_data.year is not None and (
            book_data.year < 1000 or book_data.year > datetime.now(UTC).year
        ):
            raise InvalidYearException(book_data.year)

        if book_data.pages is not None and book_data.pages < 1:
            raise InvalidPagesException(book_data.pages)

        if book_data.isbn:
            isbn_book = await self.book_repo.find_by_isbn(book_data.isbn)
            if isbn_book is not None and isbn_book.book_id != book_id:
                raise BookAlreadyExistsException(book_data.isbn)

        update_data = book_data.model_dump(exclude_unset=True)
        saved_book = await self.book_repo.update(book_id, **update_data)

        if saved_book is None:
            raise BookNotFoundException(book_id)

        return BookMapper.to_show_book(saved_book)

    async def delete_book(self, book_id: UUID) -> None:
        deleted = await self.book_repo.delete(book_id)

        if not deleted:
            raise BookNotFoundException(book_id)

    async def search_books(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ShowBook], int]:
        books = await self.book_repo.find_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            limit=limit,
            offset=offset,
            available=available,
        )
        total = await self.book_repo.count_by_filters(
            title=title, author=author, genre=genre, year=year, available=available
        )

        return BookMapper.to_show_books(books), total
