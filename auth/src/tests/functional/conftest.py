import asyncio
from dataclasses import dataclass
from typing import Optional

import aiohttp
import asyncpg
import pytest
from multidict import CIMultiDictProxy

from .settings import TestSettings

settings = TestSettings()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
async def psql_client():
    conn = await asyncpg.connect(f'postgresql://{settings.pg_user}:'
                                 f'{settings.pg_password}@'
                                 f'{settings.pg_host}/{settings.pg_db}')
    yield conn
    await conn.execute('TRUNCATE users, roles, roles_users, auth_history, '
                       'revoked_tokens CASCADE')
    await conn.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture
def make_get_request(session):
    async def inner(
        method: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        method_type: Optional[str] = None
    ) -> HTTPResponse:
        url = settings.service_url + settings.api_url + method

        if method_type == 'get':
            async with session.get(
                url, json=params, headers=headers
            ) as response:
                return HTTPResponse(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )
        elif method_type == 'put':
            async with session.put(
                url, json=params, headers=headers
            ) as response:
                return HTTPResponse(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )
        elif method_type == 'delete':
            async with session.delete(
                url, json=params, headers=headers
            ) as response:
                return HTTPResponse(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )
        else:
            async with session.post(
                url, json=params, headers=headers
            ) as response:
                return HTTPResponse(
                    body=await response.json(),
                    headers=response.headers,
                    status=response.status,
                )
    return inner
