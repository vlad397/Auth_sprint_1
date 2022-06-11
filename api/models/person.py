from pydantic import BaseModel

from core.models_config import BaseConfig


class Person(BaseModel):
    uuid: str
    full_name: str

    class Config(BaseConfig):
        pass
