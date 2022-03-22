from fastapi import Request as _Request

from ..auth import KeyManager
from ..users import UserManager


class RequestState:
    auth: KeyManager
    users: UserManager


class Request(_Request):
    state: RequestState  # type: ignore
