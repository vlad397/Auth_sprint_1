from pydantic import BaseModel
from typing import List, Optional

from .person import Person
from .genre import Genre
from core.models_config import BaseConfig


class FilmResponse(BaseModel):
    uuid: str = ""
    title: str = ""
    imdb_rating: Optional[float]

    class Config(BaseConfig):
        pass


class Film(FilmResponse):
    description: Optional[str]
    genres: List[Genre]
    directors: List[Person]
    writers: List[Person]
    actors: List[Person]


class PersonResponse(Person):
    film_ids: List[Film]
