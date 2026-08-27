from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.library_catalog.api.v1.dependencies import get_book_service
from src.library_catalog.api.v1.schemas.book import (
    BookCreate,
    BookFilters,
    BookUpdate,
    ShowBook,
)
from src.library_catalog.api.v1.schemas.common import (
    PaginatedResponse,
    PaginationParams,
)
from src.library_catalog.domain.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("", response_model=ShowBook, status_code=201)
async def create_book(
    book: BookCreate, service: Annotated[BookService, Depends(get_book_service)]
) -> ShowBook:
    return await service.create_book(book)


@router.get("/{book_id}", response_model=ShowBook, status_code=200)
async def get_book(
    book_id: UUID, service: Annotated[BookService, Depends(get_book_service)]
) -> ShowBook:
    return await service.get_book(book_id)


@router.patch("/{book_id}", response_model=ShowBook, status_code=200)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    service: Annotated[BookService, Depends(get_book_service)],
) -> ShowBook:
    return await service.update_book(book_id, book_data)


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: UUID, service: Annotated[BookService, Depends(get_book_service)]
) -> None:
    await service.delete_book(book_id)


@router.get("", response_model=PaginatedResponse[ShowBook])
async def search_books(
    filters: Annotated[BookFilters, Depends()],
    pagination: Annotated[PaginationParams, Depends()],
    service: Annotated[BookService, Depends(get_book_service)],
) -> PaginatedResponse[ShowBook]:
    books, total = await service.search_books(
        **filters.model_dump(), limit=pagination.limit, offset=pagination.offset
    )
    return PaginatedResponse.create(items=books, total=total, pagination=pagination)
