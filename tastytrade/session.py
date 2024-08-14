from dataclasses import dataclass, InitVar, field

import aiohttp

from tastytrade import APP_ENV_CONFIG
from tastytrade.exception import TastyTradeException


@dataclass
class Session:
    login: InitVar[str]
    password: InitVar[str | None]
    remember_me: InitVar[bool | None]
    remember_token: InitVar[str | None]
    sandbox: InitVar[bool | None] = False
    client: aiohttp.ClientSession = field(init=False)
    base_url: str = field(init=False)

    def __post_init__(
        self,
        login: str,
        password: str | None = None,
        remember_me: bool | None = False,
        remember_token: str | None = None,
        sandbox: bool = False,
    ) -> None:
        request_body = create_request_body(login, password, remember_me, remember_token)
        self.base_url = self._get_base_url(sandbox)

    def _get_base_url(self, sandbox: bool) -> str:
        if sandbox:
            return APP_ENV_CONFIG.get("BASE_SANDBOX_URL")

        return APP_ENV_CONFIG.get("BASE_PROD_URL")


def create_request_body(login: str, password: str, remember_me: bool, remember_token: str) -> dict[str, object]:
    if password is None and remember_me is None:
        raise TastyTradeException("A password of remember token must be provided to login.")

    request_body = {"login": login, "remember-me": remember_me}

    if password:
        request_body["password"] = password
    else:
        request_body["remember-token"] = remember_token

    return request_body
