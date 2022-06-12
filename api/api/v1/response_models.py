from lib2to3.pytree import Base
from typing import List, Optional

from pydantic import BaseModel

from core.models_config import BaseConfig


class Genre(BaseModel):
    uuid: str
    name: str

    class Config(BaseConfig):
        pass


class PersonSummary(BaseModel):
    uuid: str
    full_name: str

    class Config(BaseConfig):
        pass


class FilmSummary(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]

    class Config(BaseConfig):
        pass


class Film(FilmSummary):
    description: Optional[str]
    genres: List[Genre]
    actors: List[PersonSummary]
    writers: List[PersonSummary]
    directors: List[PersonSummary]


class Person(PersonSummary):
    film_ids: List[Film]
