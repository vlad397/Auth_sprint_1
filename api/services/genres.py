from functools import lru_cache
from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from models.genre import GenreResponse
from services.mixins import GetByIDService, ListService


class GenreService(GetByIDService, ListService):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    async def get(self, genre_id: str) -> Optional[GenreResponse]:
        try:
            doc = await self.elastic.get("genres", genre_id)
        except NotFoundError:
            return None
        return GenreResponse(**doc["_source"])

    async def list(
        self,
        page_number: int = 0,
        page_size: int = 0,
        **kwargs: dict
    ) -> List[GenreResponse]:
        data = None
        try:
            data = await self.elastic.search(
                body="{}",
                index="genres",
            )
        except NotFoundError:
            return None
        if data is None:
            return None
        return [GenreResponse(**genre["_source"])
                for genre in data['hits']['hits']]


@lru_cache
def get_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
