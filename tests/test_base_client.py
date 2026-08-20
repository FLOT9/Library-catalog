from unittest.mock import AsyncMock

import httpx
import pytest

from src.library_catalog.external.base.base_client import BaseApiClient


class FakeApiClient(BaseApiClient):
    def client_name(self) -> str:
        return "test"


@pytest.mark.asyncio
async def test_get_returns_json():
    client = FakeApiClient("https://example.com")

    response = httpx.Response(
        200,
        json={"ok": True},
        request=httpx.Request(
            "GET",
            "https://example.com/health",
        ),
    )

    client._client.request = AsyncMock(return_value=response)

    result = await client._get("/health")

    assert result == {"ok": True}
    client._client.request.assert_awaited_once_with(
        "GET",
        "https://example.com/health",
        params=None,
    )

    await client.close()

@pytest.mark.asyncio
async def test_4xx_is_not_retried():
    client = FakeApiClient(
        "https://example.com",
        retries=3,
        backoff=0,
    )

    response = httpx.Response(
        404,
        request=httpx.Request(
            "GET",
            "https://example.com/health",
        ),
    )

    client._client.request = AsyncMock(return_value=response)

    with pytest.raises(httpx.HTTPStatusError):
        await client._get("/health")

    client._client.request.assert_awaited_once()

    await client.close()

@pytest.mark.asyncio
async def test_timeout_is_retried():
    client = FakeApiClient(
        "https://example.com",
        retries=2,
        backoff=0,
    )

    response = httpx.Response(
        200,
        json={"ok": True},
        request=httpx.Request(
            "GET",
            "https://example.com/health",
        ),
    )

    client._client.request = AsyncMock(
        side_effect=[
            httpx.TimeoutException("timeout"),
            response,
        ],
    )

    result = await client._get("/health")

    assert result == {"ok": True}
    assert client._client.request.await_count == 2

    await client.close()