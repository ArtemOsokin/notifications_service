from functools import lru_cache
from typing import Tuple, Optional

import ujson
from aioredis import Redis

from app.core.config import settings
from app.db.cache.abstract import Cache

redis: Optional[Redis] = None


class RedisCache(Cache):
    def __init__(self, cache: Redis):
        self.cache = cache

    async def get(self, key: str):
        data = await self.cache.get(key)
        return ujson.loads(data) if data else data

    async def set(self, key, data: Tuple[list, int]) -> None:
        await self.cache.execute('SET', key, ujson.dumps(data), 'ex', settings.CACHE.TTL)


@lru_cache()
def get_cache():
    return RedisCache(redis)
