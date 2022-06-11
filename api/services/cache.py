import abc
from typing import Any

from aioredis import Redis


class BaseCacheStorage:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    async def async_init(self) -> Any:
        pass

    @abc.abstractmethod
    async def get_data_from_cache(self, cache_key: str) -> Any:
        pass

    @abc.abstractmethod
    async def set_data_to_cache(self, cache_key: str, cache_data: str) -> Any:
        pass


class RedisCacheStorage(BaseCacheStorage):
    def __init__(self, redis_async_instantiator) -> None:
        super().__init__()
        self.async_instantiator = redis_async_instantiator

    async def async_init(self) -> Any:  # для совместимости с возможными иными движками
        pass

    async def get_data_from_cache(self, cache_key: str) -> Any:
        redis = await self.async_instantiator()
        redis_cache_data = await redis.get(cache_key)
        redis._release_callback(redis._pool_or_conn)
        if redis_cache_data:
            return redis_cache_data.decode()

    async def set_data_to_cache(self, cache_key: str, cache_data: str, expire: int = 30) -> Any:
        redis = await self.async_instantiator()
        await redis.set(
                cache_key,
                cache_data.decode(),
                expire=expire
            )
        redis._release_callback(redis._pool_or_conn)
