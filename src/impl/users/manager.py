from datetime import datetime
from typing import Any

from cachingutils import LRUCache
from ormar import NoMatch

from ..database import User


class UserFlags:
    BANNED = 1 << 0
    ADMIN = 1 << 1


class UserManager:
    def __init__(self) -> None:
        self._cache: LRUCache[int, User] = LRUCache(max_size=1024, values={})

    async def get(self, id: int) -> User:
        if id in self._cache:
            return self._cache[id]

        user = await User.objects.get(id=id)

        self._cache[id] = user

        return user

    async def create(self, id: int, name: str, discriminator: str) -> User:
        user = User(id=id, username=name, discriminator=discriminator)

        await user.save()

        self._cache[id] = user

        return user

    async def update(self, id: int, **kwargs: Any) -> User:
        user = await self.get(id)
        user = await user.update(**kwargs, updated_at=datetime.utcnow())

        self._cache[id] = user

        return user

    async def ensure(self, id: int, name: str, discriminator: str) -> User:
        try:
            return await self.get(id)
        except NoMatch:
            return await self.create(id, name, discriminator)

    async def ban(self, id: int) -> User:
        user = await self.get(id)

        return await self.update(id, flags=user.flags | UserFlags.BANNED)

    async def unban(self, id: int) -> User:
        user = await self.get(id)

        return await self.update(id, flags=user.flags & ~UserFlags.BANNED)
