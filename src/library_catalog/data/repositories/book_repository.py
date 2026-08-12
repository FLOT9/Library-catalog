from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.book import Book
from .base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Book)

    async def find_by_isbn(self, isbn: str) -> Book | None:
        statement = select(Book).where(Book.isbn == isbn)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def find_by_filters(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Book]:
        statement = select(Book)

        if title is not None:
            statement = statement.where(Book.title.ilike(f"%{title}%"))

        if author is not None:
            statement = statement.where(Book.author.ilike(f"%{author}%"))

        if genre is not None:
            statement = statement.where(Book.genre.ilike(f"%{genre}%"))

        if year is not None:
            statement = statement.where(Book.year == year)

        if available is not None:
            statement = statement.where(Book.available == available)

        statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def count_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
    ) -> int:
        statement = select(func.count()).select_from(Book)

        if title is not None:
            statement = statement.where(Book.title.ilike(f"%{title}%"))

        if author is not None:
            statement = statement.where(Book.author.ilike(f"%{author}%"))

        if genre is not None:
            statement = statement.where(Book.genre.ilike(f"%{genre}%"))

        if year is not None:
            statement = statement.where(Book.year == year)

        if available is not None:
            statement = statement.where(Book.available == available)

        result = await self.session.execute(statement)
        return result.scalar_one()
