import asyncio
import logging
from abc import ABC, abstractmethod

import httpx


class BaseApiClient(ABC):
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        retries: int = 3,
        backoff: float = 0.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._client = httpx.AsyncClient(timeout=self.timeout)
        self.logger = logging.getLogger(self.client_name())

    @abstractmethod
    def client_name(self) -> str: ...

    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path

        return self.base_url + path

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
    ) -> dict:
        url = self._build_url(path)

        for attempt in range(self.retries):
            try:
                self.logger.debug(
                    "%s %s attempt=%s",
                    method,
                    url,
                    attempt + 1,
                )

                response = await self._client.request(method, url, params=params)
                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt == self.retries - 1:
                    raise
                wait_time = self.backoff * (2**attempt)
                self.logger.warning(
                    "Request failed, retrying in %s seconds",
                    wait_time,
                )
                await asyncio.sleep(wait_time)

            except httpx.RequestError:
                if attempt == self.retries - 1:
                    raise

                wait_time = self.backoff * (2**attempt)
                self.logger.warning(
                    "Network error, retrying in %s seconds",
                    wait_time,
                )
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as error:
                status_code = error.response.status_code
                if status_code >= 500 and attempt < self.retries - 1:
                    wait_time = self.backoff * (2**attempt)
                    self.logger.warning(
                        "Request failed, retrying in %s seconds",
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise

        raise RuntimeError("Request was not attempted because retries is 0")

    async def _get(
        self,
        path: str,
        **kwargs,
    ) -> dict:
        return await self._request("GET", path, **kwargs)
