from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.database import get_db
from ...data.repositories.book_repository import BookRepository
from ...domain.services.book_service import BookService
from ...external.openlibrary.client import OpenLibraryClient


async def get_book_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BookService:
    service = BookService(
        repository=BookRepository(session),
        openlibrary_client=get_openlibrary_client(),
    )

    return service


@lru_cache
def get_openlibrary_client() -> OpenLibraryClient:
    base_url=settings.openlibrary_base_url
    timeout = settings.openlibrary_timeout

    return OpenLibraryClient(base_url=base_url, timeout=timeout)
