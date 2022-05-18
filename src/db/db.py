import flask
from flask_sqlalchemy import SQLAlchemy

from settings import Settings


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

db = SQLAlchemy()


def init_db(app: flask.app.Flask) -> None:
    db.init_app(app)
