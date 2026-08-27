from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_isbn(value: str | None) -> str | None:
    if value is None:
        return value

    clean = value.replace("-", "").replace(" ", "")

    if not clean.replace("X", "").isdigit():
        raise ValueError("ISBN must contain only digits")

    if len(clean) not in (10, 13):
        raise ValueError("ISBN must be 10 or 13 digits")

    return clean


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=300)
    year: int
    genre: str = Field(..., min_length=1, max_length=100)
    pages: int


class BookCreate(BookBase):
    isbn: str | None = Field(None, min_length=10, max_length=20)
    description: str | None = Field(None, max_length=5000)

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, value: str | None) -> str | None:
        return normalize_isbn(value)


class BookUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    author: str | None = Field(None, min_length=1, max_length=300)
    year: int | None = None
    genre: str | None = Field(None, min_length=1, max_length=100)
    pages: int | None = None
    available: bool | None = None
    isbn: str | None = Field(None, min_length=10, max_length=20)
    description: str | None = Field(None, max_length=5000)

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, value: str | None) -> str | None:
        return normalize_isbn(value)


class ShowBook(BookBase):
    available: bool
    created_at: datetime
    updated_at: datetime
    isbn: str | None = Field(None, min_length=1, max_length=20)
    description: str | None = Field(None, max_length=5000)
    extra: dict | None = None
    book_id: UUID

    model_config = ConfigDict(from_attributes=True)


class BookFilters(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    year: int | None = None
    available: bool | None = None
