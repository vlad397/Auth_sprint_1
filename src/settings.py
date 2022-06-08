from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    host: str = Field('127.0.0.1', env='POSTGRES_HOST')
    pg_password: str = Field('123qwe', env='POSTGRES_PASSWORD')
    pg_user: str = Field('app', env='POSTGRES_USER')
    pg_db: str = Field('users', env='POSTGRES_DB')
    secret_key: str = Field('super_secret', end='SECRET_KEY')
    client_id_google: str = Field('', env='CLIENT_ID_GOOGLE')
    client_secret_google: str = Field('', env='CLIENT_SECRET_GOOGLE')
    client_id_yandex: str = Field('', env='CLIENT_ID_YANDEX')
    client_secret_yandex: str = Field('', env='CLIENT_SECRET_YANDEX')
    jwt_secret_key: str = Field('super_secret', end='JWT_SECRET_KEY')
    wsgi_host: str = Field('0.0.0.0')
    wsgi_port: int = Field(8008)
    workers: int = 3
    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')
