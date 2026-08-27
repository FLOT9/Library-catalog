import httpx

from ...domain.exceptions import (
    OpenLibraryException,
    OpenLibraryTimeoutException,
)
from ..base.base_client import BaseApiClient
from .schemas import OpenLibrarySearchResponse


class OpenLibraryClient(BaseApiClient):
    def __init__(
        self,
        base_url: str = "https://openlibrary.org",
        timeout: float = 10.0,
    ) -> None:
        super().__init__(base_url, timeout=timeout)

    def client_name(self) -> str:
        return "openlibrary"

    def _get_cover_url(self, cover_id: int | None) -> str | None:
        if not cover_id:
            return None
        return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

    def _extract_book_data(self, doc: dict) -> dict:
        result = {}

        cover_url = self._get_cover_url(doc.get("cover_i"))
        if cover_url:
            result["cover_url"] = cover_url

        if subjects := doc.get("subject"):
            result["subjects"] = subjects[:10]

        if publishers := doc.get("publisher"):
            result["publisher"] = publishers[0]

        if languages := doc.get("language"):
            result["language"] = languages[0]

        rating = doc.get("ratings_average")
        if rating is not None:
            result["rating"] = rating

        return result

    async def search_by_isbn(self, isbn: str) -> dict:
        try:
            data = await self._get(
                "/search.json",
                params={"isbn": isbn, "limit": 1},
            )

            response = OpenLibrarySearchResponse.model_validate(data)

            if not response.docs:
                return {}

            return self._extract_book_data(response.docs[0].model_dump())

        except httpx.TimeoutException:
            raise OpenLibraryTimeoutException(self.timeout)
        except httpx.HTTPError as error:
            raise OpenLibraryException(str(error))

    async def search_by_title_author(self, title: str, author: str) -> dict:
        try:
            data = await self._get(
                "/search.json",
                params={
                    "title": title,
                    "author": author,
                    "limit": 1,
                },
            )

            response = OpenLibrarySearchResponse.model_validate(data)

            if not response.docs:
                return {}

            return self._extract_book_data(response.docs[0].model_dump())

        except httpx.TimeoutException:
            raise OpenLibraryTimeoutException(self.timeout)
        except httpx.HTTPError as error:
            raise OpenLibraryException(str(error))

    async def enrich(
        self,
        title: str,
        author: str,
        isbn: str | None = None,
    ) -> dict:
        if isbn:
            data = await self.search_by_isbn(isbn)
            if data:
                return data

        return await self.search_by_title_author(title, author)
