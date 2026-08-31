from datetime import UTC, datetime
from uuid import UUID

from src.library_catalog.core.exceptions import AppException, NotFoundException


class BookNotFoundException(NotFoundException):
    def __init__(self, book_id: UUID):
        super().__init__(
            resource="Book",
            identifier=book_id,
        )


class BookAlreadyExistsException(AppException):
    def __init__(self, isbn: str):
        super().__init__(
            message=f"Book with ISBN '{isbn}' already exists",
            status_code=409,
        )


class InvalidYearException(AppException):
    def __init__(self, year: int):
        current_year = datetime.now(UTC).year
        start_year = 1000
        super().__init__(
            message=f"Invalid year '{year}'. Year must be {start_year}-{current_year}",
            status_code=400,
        )


class InvalidPagesException(AppException):
    def __init__(self, pages: int):
        super().__init__(
            message=f"Pages count must be positive, got {pages}",
            status_code=400,
        )


class OpenLibraryException(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=f"Open Library API error: {message}",
            status_code=503,
        )


class OpenLibraryTimeoutException(AppException):
    def __init__(self, timeout: float):
        super().__init__(
            message=f"Open Library API timeout after {timeout}s",
            status_code=504,
        )
