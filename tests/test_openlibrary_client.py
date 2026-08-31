from unittest.mock import AsyncMock

import pytest

from src.library_catalog.external.openlibrary.client import OpenLibraryClient


@pytest.mark.asyncio
async def test_search_by_isbn_extracts_book_data() -> None:
    client = OpenLibraryClient()
    client._get = AsyncMock(
        return_value={
            "numFound": 1,
            "docs": [
                {
                    "title": "Clean Code",
                    "cover_i": 123,
                    "subject": ["Programming"],
                    "publisher": ["Prentice Hall"],
                    "language": ["eng"],
                    "ratings_average": 4.5,
                }
            ],
        }
    )

    result = await client.search_by_isbn("9780132350884")

    assert result["cover_url"] == "https://covers.openlibrary.org/b/id/123-L.jpg"
    assert result["rating"] == 4.5

    await client.close()
