from http import HTTPStatus
from tests.functional.utils import get_cache_key

import pytest
from tests.functional.testdata.persons import EXISTING_PERSONS

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("person", EXISTING_PERSONS)
async def test_api_v1_person(
        person,
        api_v1_path,
        make_get_request,
        redis_flushall,
        redis_get_from_cache
):
    key = get_cache_key("person_details", kwargs={"person_id": person["uuid"]})

    await redis_flushall()
    empty_cache = await redis_get_from_cache(key)
    response = await make_get_request(
        path=api_v1_path,
        method="persons/" + person["uuid"],
    )
    cached = await redis_get_from_cache(key)

    assert response.status == HTTPStatus.OK
    assert response.body == person
    assert empty_cache is None
    assert eval(cached) == person


async def test_api_v1_person_ne(
    api_v1_path,
    make_get_request,
    redis_flushall,
    redis_get_from_cache
):
    fake_id = "-ne-"
    key = get_cache_key("person_details", kwargs={"person_id": fake_id})

    await redis_flushall()
    empty_cache = await redis_get_from_cache(key)
    response = await make_get_request(path=api_v1_path, method="persons/" + fake_id)
    cached = await redis_get_from_cache(key)

    assert response.status == HTTPStatus.NOT_FOUND
    assert empty_cache is None
    assert cached is None


async def test_api_v1_person_films(api_v1_path, make_get_request, redis_flushall):
    await redis_flushall()
    for _ in ["not cached", "cached"]:
        for person in EXISTING_PERSONS:
            response = await make_get_request(
                path=api_v1_path,
                method="persons/" + person["uuid"] + "/film/",
            )
            assert response.status == HTTPStatus.OK
            films = [
                {k: v for k, v in film.items() if k in ["uuid", "title", "imdb_rating"]}
                for film in person["film_ids"]
            ]
            assert sorted(films) == sorted(response.body)


async def test_search_films(api_v1_path, make_get_request, redis_flushall):
    await redis_flushall()
    query = "Zasu"
    response = await make_get_request(
        path=api_v1_path, method=f"persons/search/?query={query}"
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1

    query_in_searched_films = [
        query in person["full_name"] for person in response.body
    ]

    assert all(query_in_searched_films)
