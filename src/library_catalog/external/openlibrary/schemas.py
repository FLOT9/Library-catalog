from pydantic import BaseModel, Field


class OpenLibrarySearchDoc(BaseModel):
    title: str
    author_name: list[str] | None = Field(default=None)
    cover_i: int | None = Field(default=None)
    subject: list[str] | None = Field(default=None)
    publisher: list[str] | None = Field(default=None)
    language: list[str] | None = Field(default=None)
    ratings_average: float | None = Field(default=None)


class OpenLibrarySearchResponse(BaseModel):
    numFound: int
    docs: list[OpenLibrarySearchDoc]
