import re
from http import HTTPStatus

import werkzeug
from flask import session, url_for
from jsonschema import draft4_format_checker
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

import config
from db.db import db
from db.db_models import User


@draft4_format_checker.checks('email')
def is_email(val: str) -> (re.Match[str] | None):
    """Проверка валидности почтв"""
    return re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', val)


@draft4_format_checker.checks('password')
def is_valid_password(val: str) -> (re.Match[str] | None):
    """Проверка валидности пароля"""
    pattern = (r'^(?=\S{6,20}$)(?=.*?\d)(?=.*?[a-z])'
               r'(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])')
    return re.match(pattern, val)


def register(body: dict) -> tuple[str, HTTPStatus]:
    """Функция для стандартной регистрации"""
    try:
        user = User(
            first_name=body['first_name'], second_name=body['second_name'],
            login=body['login'], email=body['email'],
            password=generate_password_hash(body['password'])
        )
        db.session.add(user)
        db.session.commit()
        return 'Successfully registered', HTTPStatus.CREATED
    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            return 'User already exists', HTTPStatus.BAD_REQUEST
        else:
            return 'Unexpected error', HTTPStatus.BAD_REQUEST


def register_oauth(provider: str) -> werkzeug.wrappers.response.Response:
    """Функция для регистрации через OAuth Google,
    перенаправляет в registerauthorize для авторизации через Google"""
    google = config.oauth.create_client('google')
    redirect_uri = url_for('/api/v1.app_api_v1_registration_registerauthorize',
                           _external=True)
    return google.authorize_redirect(redirect_uri)


def registerauthorize() -> tuple[str, HTTPStatus]:
    """Функция для регистрации через OAuth Google"""
    google = config.oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user_info = resp.json()
    user = config.oauth.google.userinfo()

    try:
        user = User(
                first_name=user['given_name'], second_name=user['family_name'],
                login=user['email'], email=user['email'], password=None
        )
        db.session.add(user)
        db.session.commit()
    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            return 'User already exists', HTTPStatus.BAD_REQUEST

    return 'Registered successfully', HTTPStatus.CREATED


def login(provider: str) -> werkzeug.wrappers.response.Response:
    """Функция для входа через OAuth Google,
    перенаправляет в loginauthorize для авторизации через Google"""
    google = config.oauth.create_client('google')
    redirect_uri = url_for('/api/v1.app_api_v1_registration_loginauthorize',
                           _external=True)
    return google.authorize_redirect(redirect_uri)


def loginauthorize() -> tuple[str, HTTPStatus]:
    """Функция для входа через OAuth Google"""
    google = config.oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user_info = resp.json()
    user = config.oauth.google.userinfo()
    if db.session.query(
        db.exists().where(User.email == user['email'])
    ).scalar():
        session['profile'] = user_info
        session.permanent = True
        return 'Logged in', HTTPStatus.OK
    return 'No such user', HTTPStatus.BAD_REQUEST


def logout_oauth() -> None:
    """Функция выхода из аккаунта"""
    for key in list(session.keys()):
        session.pop(key)


def main_func() -> str:
    """Функция для теста, будет убрана"""
    try:
        email = dict(session)['profile']['email']
    except KeyError:
        email = 'NOBODY!!!'
    return f'Hello, you are logged in as {email}!'
