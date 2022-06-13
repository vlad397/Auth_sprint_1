from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    host: str = Field('127.0.0.1', env='POSTGRES_HOST')
    port: int = Field(5432, env='POSTGRES_PORT')
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
    google_access_token_url: str = Field(
        'https://accounts.google.com/o/oauth2/token', end='GATU')
    google_authorize_url: str = Field(
        'https://accounts.google.com/o/oauth2/auth', end='GAU')
    google_api_base_url: str = Field(
        'https://www.googleapis.com/oauth2/v1/', end='GABU')
    google_userinfo_endpoint: str = Field(
        'https://openidconnect.googleapis.com/v1/userinfo', end='GUE')
    google_client_kwargs: str = Field('openid email profile')
    yandex_userinfo_endpoint: str = Field(
        'https://login.yandex.ru/info', end='YUE')
    yandex_access_token_url: str = Field(
        'https://oauth.yandex.ru/token', end='YATU')
    yandex_authorize_url: str = Field(
        'https://oauth.yandex.ru/authorize', end='YAU')
    yandex_api_base_url: str = Field(
        'https://oauth.yandex.ru', end='YABU')
