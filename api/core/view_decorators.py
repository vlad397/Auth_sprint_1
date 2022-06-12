from functools import wraps
import re

from services.cache import RedisCacheStorage, BaseCacheStorage
import orjson
from pydantic import BaseModel, parse_raw_as

from db.redis import get_redis


# review: чуть более SOLID-но: сделать абстрактный cache,
# инжектируея/параметризуя его абстрактным engine,
# методами которого оперировать внутри реализации
def url_cache(
    expire: int = 30,
    storage: BaseCacheStorage = RedisCacheStorage(get_redis)
):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            await storage.async_init()
            kwargs_copy = kwargs.copy()
            string_kwargs = str(kwargs_copy)
            service_key_name = re.search(r"\w*_service", string_kwargs)

            if service_key_name.group(0):
                kwargs_copy.pop(service_key_name.group(0))

            cache_key = func.__name__ + "="
            for k, v in kwargs_copy.items():
                cache_key += "::" + str(k) + "::" + str(v)

            return_type = func.__annotations__["return"]
            if not return_type:
                return await func(*args, **kwargs)

            cache_data = await storage.get_data_from_cache(cache_key)
            if cache_data:
                return parse_raw_as(return_type, cache_data)

            data = await func(*args, **kwargs)

            if not isinstance(data, BaseModel):
                data_in_redis_format = orjson.dumps([part.dict() for part in data])
            else:
                data_in_redis_format = orjson.dumps(data.dict())

            await storage.set_data_to_cache(
                cache_key, data_in_redis_format, expire=expire
            )

            return data

        return inner

    return wrapper
