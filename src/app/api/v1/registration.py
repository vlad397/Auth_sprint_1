import connexion
import psycopg2
from db.db import db_session
from db.db_models import User
from werkzeug.security import generate_password_hash, check_password_hash
import re
from jsonschema import draft4_format_checker
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation


@draft4_format_checker.checks('email')
def is_email(val):
    return re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', val)

def register(body):
    try:
        user = User(
            first_name=body['first_name'], second_name=body['second_name'],
            login=body['login'], email=body['email'],
            password=generate_password_hash(body['password'])
        )
        db_session.add(user)
        db_session.commit()
        return 'Successfully registered', 201
    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            return 'User already exists', 400

