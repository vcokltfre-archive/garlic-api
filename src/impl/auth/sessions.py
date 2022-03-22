from datetime import datetime, timedelta
from os import environ
from secrets import token_hex
from typing import Optional, TypedDict

from cachingutils import Cache, LRUCache
from jose.jwt import decode, encode
from ormar import NoMatch

from ..database import AccessKey, User
from ..users import UserFlags, UserManager


class KeyJWT(TypedDict):
    k: int


class KeyManager:
    def __init__(self, user_manager: UserManager) -> None:
        self._user_manager = user_manager
        self._cache: LRUCache[int, AccessKey] = LRUCache(max_size=1024, values={})
        self._handoff: Cache[str, int] = Cache(values={}, timeout=30)

    async def _get(self, id: int) -> AccessKey:
        if id in self._cache:
            return self._cache[id]

        key = await AccessKey.objects.get(id=id)

        self._cache[id] = key

        return key

    async def get(self, id: int) -> tuple[AccessKey, User]:
        key = await self._get(id)

        if key.valid_until < datetime.utcnow():
            del self._cache._items[id]  # type: ignore

            raise NoMatch()

        try:
            user = await self._user_manager.get(key.user_id)
        except NoMatch as e:
            raise e

        if user.flags & UserFlags.BANNED:
            raise NoMatch()

        return key, user

    async def create(self, user_id: int, valid_from: datetime, valid_until: datetime) -> tuple[str, AccessKey]:
        key = AccessKey(user_id=user_id, valid_from=valid_from, valid_until=valid_until)

        await key.save()

        self._cache[key.id] = key

        return encode({"k": key.id}, environ["JWT_SECRET"], algorithm="HS256"), key

    async def decode(self, token: str) -> Optional[User]:
        try:
            payload: KeyJWT = decode(token, environ["JWT_SECRET"], algorithms="HS256")  # type: ignore
        except Exception:
            return

        try:
            _key, user = await self.get(payload["k"])
        except NoMatch:
            return

        return user

    async def generate_handoff(self, user_id: int) -> str:
        handoff = token_hex(64)

        self._handoff[handoff] = user_id

        return handoff

    async def from_handoff(self, token: str) -> Optional[tuple[str, AccessKey]]:
        try:
            user_id = self._handoff[token]
        except KeyError:
            return

        return await self.create(user_id, datetime.utcnow(), datetime.utcnow() + timedelta(days=7))
