from dataclasses import dataclass, field, InitVar
from typing import Self

import aiohttp
from fake_useragent import UserAgent

from tastytrade import APP_ENV_CONFIG


@dataclass
class TastyClient:
    sandbox: InitVar[bool] = False
    base_url: str = field(init=False)
    headers: dict[str, str] = field(init=False)
    session: aiohttp.ClientSession = field(init=False)

    def __post_init__(self, sandbox: bool) -> None:
        self.base_url = _get_base_url(sandbox)
        self.headers = _get_default_headers()
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def _request(self, method: str, endpoint: str, **kwargs: object) -> object:
        url = f"{self.base_url}{endpoint.lstrip('/')}"

        async with self.session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    async def get(self, endpoint: str, params: dict[str, str] | None = None) -> object:
        return await self._request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, data: dict[str, str] | None = None, json: dict[str, str] | None = None
    ) -> object:
        return await self._request("POST", endpoint, json=json, data=data)

    async def put(
        self, endpoint: str, data: dict[str, str] | None = None, json: dict[str, str] | None = None
    ) -> object:
        return await self._request("PUT", endpoint, json=json, data=data)

    async def delete(self, endpoint: str, params: dict[str, str] | None = None) -> object:
        return await self._request("DELETE", endpoint, params=params)

    async def close(self) -> None:
        if not self.session.closed:
            await self.session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


def _get_base_url(sandbox: bool) -> str:
    if sandbox:
        url = APP_ENV_CONFIG.get("BASE_SANDBOX_URL")
    else:
        url = APP_ENV_CONFIG.get("BASE_PROD_URL")

    return url.rstrip("/")


def _get_default_headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": UserAgent().random,
    }
