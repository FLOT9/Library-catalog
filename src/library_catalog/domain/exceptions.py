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
