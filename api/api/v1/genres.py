from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from services.genres import get_service
from services.mixins import GetByIDService, ListService
from api.v1.response_models import Genre
from core.view_decorators import url_cache

import core.messages as messages

router = APIRouter()


@router.get(
    '/',
    response_model=List[Genre],
    summary = "Получение списка жанров",
    description = "Полный список жанров, без разделения на страницы (жанров немного)",
    response_description = "Список из названий и идентификаторов жанров",
    tags = ['Список жанров']
)
@url_cache(expire=120)
async def genres(
    genre_service: ListService = Depends(get_service)
) -> List[Genre]:
    genres_list = await genre_service.list()
    if genres_list is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=messages.GENRES_NOT_FOUND
        )
    return [Genre.parse_obj(genre) for genre in genres_list]


@router.get(
    '/{genre_id}',
    response_model=Genre,
    summary="Получение свдений о жанре",
    description="Получить название и идентификатор жанра по уже известному идентификатору",
    response_description="Название и идентификатор жанра",
    tags=['Сведения о жанре']
)
@url_cache(expire=120)
async def genre_details(
        genre_id: str,
        genre_service: GetByIDService = Depends(get_service)
) -> Genre:
    genre = await genre_service.get(genre_id)
    if genre is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=messages.GENRE_NOT_FOUND
        )
    return Genre.parse_obj(genre)
