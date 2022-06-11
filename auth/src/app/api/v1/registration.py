import re
from http import HTTPStatus

from flask import url_for
from jsonschema import draft4_format_checker
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from werkzeug.wrappers.response import Response

import config
from app.response_messages import ReqMessage
from db.db import db
from db.db_models import User

from .basics import basic_oauth_register_authorization


@draft4_format_checker.checks('email')
def is_email(val: str) -> (re.Match[str] | None):
    """Проверка валидности почты"""
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
        return ReqMessage.SUCCESS_REG, HTTPStatus.CREATED

    # Если возникла ошибка уникальности - такой юзер уже есть
    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            return ReqMessage.USER_EXIST, HTTPStatus.BAD_REQUEST
        else:
            return ReqMessage.UNEXPECTED_ERROR, HTTPStatus.BAD_REQUEST


def register_oauth(provider: str) -> Response | tuple[str, HTTPStatus]:
    """Функция для регистрации через OAuth Google,
    перенаправляет в register_authorize_google для авторизации через Google"""
    # Если указали несуществуюую соц сеть - ошибка
    if provider not in ['google', 'yandex']:
        return ReqMessage.SOCIAL_NOT_FOUND, HTTPStatus.BAD_REQUEST

    social = config.oauth.create_client(provider)
    redirect_uri = url_for(
        f'/api/v1.app_api_v1_registration_register_authorize_{provider}',
        _external=True
    )
    return social.authorize_redirect(redirect_uri)


def register_authorize_google() -> tuple[str | dict, HTTPStatus]:
    """Функция для авторизации через OAuth Google"""
    google = config.oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user = resp.json()

    #  Если после авторизации в гугле информация пустая - пробуем иначе
    if not user:
        user = config.oauth.google.userinfo()

    # Если после авторизации в гугле информация все еще пустая - ошибка
    if not user:
        return ReqMessage.SOMETHING_WENT_WRONG, HTTPStatus.BAD_REQUEST

    return basic_oauth_register_authorization(user, 'google')


def register_authorize_yandex() -> tuple[str | dict, HTTPStatus]:
    """Функция для авторизации через OAuth Yandex"""
    yandex = config.oauth.create_client('yandex')
    token = yandex.authorize_access_token()
    user = yandex.get('userinfo', token=token)

    # Если после авторизации в яндексе информация пустая - пробуем иначе
    if not user:
        user = dict(config.oauth.yandex.userinfo())

    # Если все равно нет информации - ошибка
    if not user:
        return ReqMessage.SOMETHING_WENT_WRONG, HTTPStatus.BAD_REQUEST

    return basic_oauth_register_authorization(user, 'yandex')
