from uuid import UUID

from ...api.v1.schemas.book import ShowBook
from ...data.repositories.book_repository import BookRepository
from ..exceptions import BookNotFoundException
from ..mappers.book_mapper import BookMapper


class BookService:
    def __init__(self, repository: BookRepository) -> None:
        self.book_repo = repository

    async def get_book(self, book_id: UUID) -> ShowBook:
        book = await self.book_repo.get_by_id(book_id)

        if book is None:
            raise BookNotFoundException(book_id)

        return BookMapper.to_show_book(book)
