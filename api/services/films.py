from functools import lru_cache
import re
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from services.mixins import GetByIDService, ListService, SearchService
from fastapi import Depends

from core.elastic_queries_films import (
    get_filter_genre_query,
    get_search_film_query,
)
from db.elastic import get_elastic
from models.film import Film, FilmResponse


# review: more SOLID-like: напрашиватся общая идея о функциональных
# абстрациях GetByIDService, ListService и SearchService
# при этом, с учетом того, что перехода с ElasticSearch на что-то
# иное в ближайшие N лет явно не планируется, то можно оставить его
# как есть, не абстрагируя
class FilmService(GetByIDService, SearchService, ListService):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    async def get(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc["_source"])

    async def list(
        self,
        page_number: int = 0,
        page_size: int = 0,
        **kwargs: dict
    ) -> Optional[List[FilmResponse]]:
        try:
            query = dict()
            sort_in_elastic_terms = None

            sort: str = kwargs['sort']
            filter_genre = kwargs['filter_genre']

            if sort:
                if sort.startswith("-"):
                    sort_in_elastic_terms = f"{sort.removeprefix('-')}:desc"
                elif sort.startswith("_"):
                    sort_in_elastic_terms = f"{sort.removeprefix('_')}:desc"
                else:
                    sort_in_elastic_terms = f"{sort}:asc"

            if filter_genre:
                filter_genre_query = get_filter_genre_query(filter_genre)
                query.update(filter_genre_query)

            from_ = page_number * page_size - page_number
            data = await self.elastic.search(
                body=query,
                index="movies",
                sort=sort_in_elastic_terms,
                from_=from_,
                size=page_number,
            )
        except NotFoundError:
            return None
        docs = data["hits"]["hits"]
        return [FilmResponse(**doc["_source"]) for doc in docs]

    async def search(
        self,
        string: str,
        page_number: int = 0,
        page_size: int = 50,
        **kwargs: dict
    ) -> Optional[List[FilmResponse]]:
        try:
            if not string:
                return None

            search_query = get_search_film_query(string)

            from_ = page_number * page_size - page_number
            data = await self.elastic.search(
                body=search_query,
                index="movies",
                from_=from_,
                size=page_number,
            )
        except NotFoundError:
            return None
        docs = data["hits"]["hits"]
        return [FilmResponse(**doc["_source"]) for doc in docs]


@lru_cache
def get_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
