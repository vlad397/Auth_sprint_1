from http import HTTPStatus
import random
from tests.functional.utils import get_cache_key

import pytest

from tests.functional.testdata.films import ONE_FILM

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "page, size", [
        ('', ''),
        ("-1", "-1"),
        ("0", "0"),
        ("1000000", "100000"),
        ("1", "1"),
        ("2", "50")
    ]
)
async def test_get_all_films_with_pagination(
    page,
    size,
    api_v1_path,
    make_get_request,
    redis_flushall,
    redis_get_from_cache
):
    kwargs = {'sort': '', 'filter_genre': '', 'page': page, 'size': size}
    key = get_cache_key("films", kwargs=kwargs)

    await redis_flushall()
    empty_cache = await redis_get_from_cache(key)
    response = await make_get_request(path=api_v1_path, method="films/", params=kwargs)
    cached = await redis_get_from_cache(key)

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 50
    assert all(response.body)
    assert empty_cache is None
    assert response.body == eval(cached) if cached is not None else True


@pytest.mark.parametrize("film", [ONE_FILM])
async def test_get_one_film(
    film,
    api_v1_path,
    make_get_request,
    redis_flushall,
    redis_get_from_cache
):
    kwargs = {'film_id': film['uuid']}
    key = get_cache_key("film_details", kwargs=kwargs)

    await redis_flushall()
    empty_cache = await redis_get_from_cache(key)
    response = await make_get_request(
        path=api_v1_path, method="films/" + film["uuid"]
    )
    cached = await redis_get_from_cache(key)

    assert response.status == HTTPStatus.OK
    assert response.body == film
    assert empty_cache is None
    assert eval(cached) == film


async def test_get_not_exist_film(
    api_v1_path,
    make_get_request,
    redis_flushall,
    redis_get_from_cache
):
    fake_id = '-ne-'
    kwargs = {'film_id': fake_id}
    key = get_cache_key("film_details", kwargs=kwargs)

    await redis_flushall()
    empty_cache = await redis_get_from_cache(key)
    response = await make_get_request(
        path=api_v1_path, method="films/" + fake_id
    )
    cached = await redis_get_from_cache(key)

    assert response.status == HTTPStatus.NOT_FOUND
    assert cached is None
    assert empty_cache is None


async def test_get_film_sorted(api_v1_path, make_get_request, redis_flushall):
    await redis_flushall()
    response = await make_get_request(
        path=api_v1_path, method="films?sort=-imdb_rating"
    )
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 50
    ratings = [film["imdb_rating"] for film in response.body]

    assert sorted(ratings, reverse=True) == ratings


async def test_get_filtered_films(api_v1_path, make_get_request, redis_flushall):
    await redis_flushall()
    response = await make_get_request(
        path=api_v1_path, method="films?filter[genre]=1cacff68-643e-4ddd-8f57-84b62538081a"
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 50

    random_film = random.choice(response.body)

    film_response = await make_get_request(
        path=api_v1_path, method="films/" + random_film['uuid']
    )

    genres = [genre['name'] for genre in film_response.body['genres']]

    assert "Drama" in genres


async def test_search_films(api_v1_path, make_get_request, redis_flushall):
    await redis_flushall()
    query = "star"
    response = await make_get_request(
        path=api_v1_path, method=f"films/search/?query={query}"
    )

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 50

    query_in_searched_films = [query in film['title'].lower() for film in response.body]

    assert any(query_in_searched_films)
