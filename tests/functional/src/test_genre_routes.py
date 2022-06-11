from http import HTTPStatus
import pytest

from tests.functional.testdata.genres import ONE_GENRE


pytestmark = pytest.mark.asyncio


async def test_get_all_genres(api_v1_path, make_get_request, redis_flushall):
    await redis_flushall()
    response = await make_get_request(path=api_v1_path, method="genres/")
    assert response.status == HTTPStatus.OK
    assert all(response.body)


async def test_get_one_genre(api_v1_path, make_get_request, redis_flushall):
    await redis_flushall()
    response = await make_get_request(
        path=api_v1_path, method="genres/" + ONE_GENRE["uuid"]
    )
    assert response.status == HTTPStatus.OK
    assert response.body == ONE_GENRE


async def test_get_not_exist_genre(api_v1_path, make_get_request, redis_flushall):
    await redis_flushall()
    response = await make_get_request(
        path=api_v1_path, method="genres/not_exist-genre"
    )
    assert response.status == HTTPStatus.NOT_FOUND
