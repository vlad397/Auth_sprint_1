import aiohttp
import asyncio
import pytest
from tests.functional.settings import (
    API_HOST,
    API_PATH_V1,
    ELASTICSEARCH_ADDRESS,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
)

from typing import Optional
from dataclasses import dataclass
from multidict import CIMultiDictProxy
from elasticsearch import AsyncElasticsearch
import aioredis


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()


@pytest.fixture(scope='session')
async def redis():
    client = await aioredis.create_redis_pool(
        (REDIS_HOST, REDIS_PORT),
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        minsize=10,
        maxsize=20
    )
    yield client
    client.close()
    await client.wait_closed()


@pytest.fixture(scope='session')
async def elastic():
    client = AsyncElasticsearch(hosts=eval(ELASTICSEARCH_ADDRESS))
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session():
    connector = aiohttp.TCPConnector(limit=10)
    session = aiohttp.ClientSession(connector=connector)
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(path: str, method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        uri = path + method
        async with session.get(uri, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


@pytest.fixture
def redis_flushall(redis):
    async def inner() -> None:
        return await redis.flushall()
    return inner


@pytest.fixture
def redis_get_from_cache(redis):
    async def inner(key: str) -> None:
        redis_cache_data = await redis.get(key)
        if redis_cache_data:
            return redis_cache_data.decode()
        return None
    return inner


@pytest.fixture
def api_v1_path():
    return API_HOST + API_PATH_V1
