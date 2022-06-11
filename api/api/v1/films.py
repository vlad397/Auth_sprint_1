from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import parse_obj_as

from core.view_decorators import url_cache
from services.films import get_service
from services.mixins import GetByIDService, ListService, SearchService
from api.v1.response_models import Film, FilmSummary

import core.messages as messages

router = APIRouter()


@router.get(
    "/",
    response_model=List[FilmSummary],
    summary="Получение списка кинопроизведений",
    description="Постраничный список известных сервису кинопроизведений в краткой форме",
    response_description="Название, идентификатор и IMDB-рейтинг фильма",
    tags=['Список кинопроизведений']
)
@url_cache(expire=60)
async def films(
    sort: Optional[str] = Query(None),
    filter_genre: Optional[str] = Query(None, alias="filter[genre]"),
    page: Optional[int] = Query(1, alias="page[number]"),
    size: Optional[int] = Query(50, alias="page[size]"),
    film_service: ListService = Depends(get_service),
) -> List[FilmSummary]:
    films = await film_service.list(
        page_number=size, page_size=page, sort=sort, filter_genre=filter_genre
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=messages.FILMS_NOT_FOUND
        )
    return parse_obj_as(List[FilmSummary], films)


@router.get(
    "/{film_id}",
    response_model=Film,
    summary="Получение сведений о конкретном кинопроизведении",
    description="Полный набор сведений о конкретном кинопроизвдении,"
                "включая сведения о жанрах, актерах и режиссерах",
    response_description="Название, описание, IMDB-рейтинг, актеры, режиссеры, жанры",
    tags=['Полная информация о кинопроизведении']
)
@url_cache(expire=60)
async def film_details(
    film_id: str,
    film_service: GetByIDService = Depends(get_service)
) -> Film:
    film = await film_service.get(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=messages.FILM_NOT_FOUND
        )
    return Film(**film.dict())


@router.get(
    "/search/",
    response_model=List[FilmSummary],
    summary="Поиск кинопроизведений",
    description="Поиск кинопроизведений по указанной строке " +
                "запроса с постраничным выводом результатов в краткой форме",
    response_description="Идентификатор фильма, название, и IMDB-рейтинг",
    tags=['Поиск кинопроизведения']
)
@url_cache(expire=60)
async def search_films(
    query: Optional[str] = Query(None),
    page: Optional[int] = Query(1, alias="page[number]"),
    size: Optional[int] = Query(50, alias="page[size]"),
    film_service: SearchService = Depends(get_service),
) -> List[FilmSummary]:
    films = await film_service.search(
        string=query,
        page_number=size,
        page_size=page
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=messages.FILMS_NOT_FOUND
        )
    return parse_obj_as(List[FilmSummary], films)
