from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from services.persons import get_service
from api.v1.response_models import Person, FilmSummary
from services.mixins import GetByIDService, SearchService
from typing import List, Optional
from core.view_decorators import url_cache
import core.messages as messages

router = APIRouter()


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Получение свдений о персоне",
    description="Возвращает полный набор сведений о конкретной персоне (включая данные о фильмах)",
    response_description="Сведения о персоне (включая данные о фильмах)",
    tags=['Сведения о персонах']
)
@url_cache(expire=60)
async def person_details(
    person_id: str,
    person_service: GetByIDService = Depends(get_service)
) -> Person:
    person = await person_service.get(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=messages.PERSON_NOT_FOUND
        )
    return Person.parse_obj(person)


@router.get(
    "/{person_id}/film/",
    response_model=List[FilmSummary],
    summary="Получение данных о фильмах с участием персоны",
    description="Возвращает все фильмы, в которых персона принимала" +
                "участие как актер, режиссер или сценарист (без возможности постраничного вывода)",
    response_description="Список фильмов со всей информацией",
    tags=['Сведения о фильмах с участием персоны']
)
@url_cache(expire=60)
async def person_films_short_summary(
    person_id: str,
    person_service: GetByIDService = Depends(get_service)
) -> List[FilmSummary]:
    person = await person_service.get(person_id)
    if person is None or len(person.film_ids) == 0:  # спекулятивно, но в одну строчку
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=messages.FILMS_NOT_FOUND
        )
    return [FilmSummary.parse_obj(film) for film in person.film_ids]


@router.get(
    "/search/",
    response_model=List[Person],
    summary="Поиск персон по заданой строке",
    description="Возвращает полный набор сведений персонах," +
                "найденных по искомой строке, с постраничным разбиением",
    response_description="Сведения о найденных персонах (включая данные о фильмах)",
    tags=['Поиск персон']
)
@url_cache(expire=60)
async def search_persons(
    query: Optional[str] = Query(None),
    page: Optional[int] = Query(1, alias="page[number]"),
    size: Optional[int] = Query(50, alias="page[size]"),
    person_service: SearchService = Depends(get_service)
) -> List[Person]:
    persons = await person_service.search(
        search_text=query,
        page_number=page,
        page_size=size
    )
    if not persons:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=messages.PERSONS_NOT_FOUND
        )
    return [Person.parse_obj(person) for person in persons]
