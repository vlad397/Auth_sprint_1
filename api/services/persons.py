from functools import lru_cache
from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from models.person import Person
from models.film import PersonResponse, FilmResponse
from core.elastic_queries_persons import (
    get_persons_movies_query,
    get_persons_search_query
)
from services.mixins import GetByIDService, SearchService


# review from MatMerd: считаю, что нужно чуть более понятное название переменным в функции appends_films_to person
class PersonService(GetByIDService, SearchService):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    async def get(self, person_id: str) -> Optional[PersonResponse]:
        person, films = None, None
        try:
            person = await self._person_from_elastic(person_id, raw=True)
            if person is None:
                return None
            films = await self.elastic.search(
                body=get_persons_movies_query([person_id]),
                index="movies",
                from_=0,
                size=10000,  # да, мы поместимся :)
            )
        except NotFoundError:
            return None
        films = [film['_source'] for film in films['hits']['hits']]
        person['film_ids'] = films
        return PersonResponse(**person)

    async def search(
            self,
            search_text: str,
            page_number: int = 0,
            page_size: int = 50,
            **kwargs: dict
    ) -> Optional[List[PersonResponse]]:
        try:
            if not search_text:
                return None
            persons = await self._paginate_persons_from_elastic(
                page_number,
                page_size,
                search_text=search_text
            )
            if not persons:
                return None
        except NotFoundError:
            return None
        return persons

    async def _person_from_elastic(
            self,
            person_id: str,
            raw: bool = False
    ) -> Optional[Person]:
        try:
            doc = await self.elastic.get("persons", person_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"]) if not raw else doc["_source"]

    def _append_films_to_persons(self, persons_data: list, films: list):
        person_ids_2_movies_ids_set, movies_ids_2_movie_object = {}, {}
        for film in films:
            movies_ids_2_movie_object[film['uuid']] = film
            for roles in ["actors", "directors", "writers"]:
                for entry in film[roles]:
                    pid = entry['uuid']
                    if pid not in person_ids_2_movies_ids_set:
                        person_ids_2_movies_ids_set[pid] = set()
                    person_ids_2_movies_ids_set[pid].add(film['uuid'])
        for person in persons_data:
            mids = list(person_ids_2_movies_ids_set[person['uuid']])
            person['film_ids'] = [movies_ids_2_movie_object[mid] for mid in mids]

    async def _paginate_persons_from_elastic(
            self,
            page: int,
            size: int,
            search_text: str = None,
    ) -> List[PersonResponse]:
        try:
            search_query = get_persons_search_query(search_text)
            from_ = size * (page - 1 if page - 1 > 0 else 0)
            # TODO: сортирвка для единого порядка следования данных
            data = await self.elastic.search(
                body=search_query,
                index="persons",
                from_=from_,
                size=size,
            )
            if data is None:
                return None
            persons = [person['_source'] for person in data['hits']['hits']]
            person_ids = [person['uuid'] for person in persons]
            films = await self.elastic.search(
                body=get_persons_movies_query(person_ids),
                index="movies",
                from_=0,
                size=10000,  # лимитировать page size, чтобы уместиться
            )
            if films is None:
                films = []
            else:
                films = [film['_source'] for film in films['hits']['hits']]
            self._append_films_to_persons(persons, films)
        except NotFoundError:
            return None
        return [PersonResponse(**person) for person in persons]


@lru_cache
def get_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
