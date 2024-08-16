import asyncio
from dataclasses import dataclass, field, InitVar
from typing import Self, Any
from urllib.parse import urljoin

import aiohttp
from fake_useragent import UserAgent

from tastytrade import APP_ENV_CONFIG, LOGGER

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0


@dataclass
class TastyTradeClient:
    sandbox: InitVar[bool] = False
    session: aiohttp.ClientSession = None
    base_url: str = field(init=False)
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_delay: float = DEFAULT_RETRY_DELAY

    def __post_init__(self, sandbox: bool) -> None:
        self.base_url = _get_base_url(sandbox)

    @classmethod
    async def create(cls, sandbox: bool) -> Self:
        self = cls(sandbox=sandbox)
        self.session = aiohttp.ClientSession(
            raise_for_status=True, headers=_get_default_headers()
        )
        return self

    async def close(self) -> None:
        if self.session and not self.session.closed:
            return await self.session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        url = urljoin(self.base_url, endpoint)

        for attempt in range(self.max_retries):
            return await self._request_attempt(attempt, method, url, **kwargs)

    async def _request_attempt(
        self, attempt: int, method: str, url: str, **kwargs: Any
    ) -> Any:
        try:
            LOGGER.debug(f"Sending {method} request to {url}.")

            async with self.session.request(method, url, **kwargs) as response:
                data = await response.json()
                LOGGER.debug(f"Received response: {data}")
                return data
        except aiohttp.ClientResponseError as e:
            LOGGER.error(f"Request failed: {e}", exc_info=True, stack_info=True)

            if attempt == self.max_retries - 1:
                raise
            await asyncio.sleep(self.retry_delay * (2**attempt))

    async def get(self, endpoint: str, params: dict | None = None) -> Any:
        return await self._request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, data: dict | None = None, json: dict | None = None
    ) -> Any:
        return await self._request("POST", endpoint, json=json, data=data)

    async def put(
        self, endpoint: str, data: dict | None = None, json: dict | None = None
    ) -> Any:
        return await self._request("PUT", endpoint, json=json, data=data)

    async def delete(self, endpoint: str, params: dict | None = None) -> Any:
        return await self._request("DELETE", endpoint, params=params)


def _get_base_url(sandbox: bool) -> str:
    if sandbox:
        return APP_ENV_CONFIG.get("BASE_SANDBOX_URL")

    return APP_ENV_CONFIG.get("BASE_PROD_URL")


def _get_default_headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": UserAgent().random,
    }
