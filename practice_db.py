import asyncio
from uuid import UUID

from src.library_catalog.core.database import async_session_maker
from src.library_catalog.data.repositories.book_repository import BookRepository


async def main() -> None:
    async with async_session_maker() as session:
        repository = BookRepository(session)

        total = await repository.count_by_filters(
            author="vladislav",
            genre="fantasy",
        )

        print("Найдено:", total)


if __name__ == "__main__":
    asyncio.run(main())
