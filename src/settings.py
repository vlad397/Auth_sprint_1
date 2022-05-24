from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    host: str = Field('127.0.0.1', env='HOST')
    port: int = Field(5000, env='PORT')
    pg_password: str = Field('123qwe', env='POSTGRES_PASSWORD')
    pg_user: str = Field('app', env='POSTGRES_USER')
    pg_db: str = Field('users', env='POSTGRES_DB')
    secret_key: str = Field('super_secret', end='SECRET_KEY')
    client_id: str = Field('', env='CLIENT_ID')
    client_secret: str = Field('', env='CLIENT_SECRET')
    jwt_secret_key: str = Field('super_secret', end='JWT_SECRET_KEY')