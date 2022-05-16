from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    host: str = Field('127.0.0.1', env='HOST')
    port: int = Field(8000, env='PORT')
    pg_password: str = Field('123qwe', env='POSTGRES_PASSWORD')
    pg_user: str = Field('app', env='POSTGRES_USER')
    pg_db: str = Field('users', env='POSTGRES_DB')