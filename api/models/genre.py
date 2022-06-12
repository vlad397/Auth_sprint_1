from pydantic import BaseModel

from core.models_config import BaseConfig

class GenreResponse(BaseModel):
    uuid: str
    name: str

    class Config(BaseConfig):
        pass


class Genre(GenreResponse):
    pass
