from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    pg_password: str = Field('123qwe', env='POSTGRES_PASSWORD')
    pg_user: str = Field('app', env='POSTGRES_USER')
    pg_db: str = Field('users', env='POSTGRES_DB')
    pg_host: str = Field('db', env='POSTGRES_HOST')
    service_url: str = Field('http://auth_app:8008')
    api_url: str = Field('/api/v1')
