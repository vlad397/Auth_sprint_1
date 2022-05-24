import re
from http import HTTPStatus

from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required)
from jsonschema import draft4_format_checker
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from db.db import db
from db.db_models import RevokedTokenModel, User


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
            password=generate_password_hash(body['password']),
            role=None
        )
        db.session.add(user)
        db.session.commit()
        return 'Successfully registered', HTTPStatus.CREATED
    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            return 'User already exists', HTTPStatus.BAD_REQUEST
        else:
            return 'Unexpected error', HTTPStatus.BAD_REQUEST


def login(body: dict) -> tuple[str | dict, HTTPStatus]:
    """Функция входа в аккаунт"""
    user = db.session.query(User).filter(User.email == body['email']).first()
    if not user:
        return 'No such user', HTTPStatus.NOT_FOUND

    if check_password_hash(user.password, body['password']):
        claims = {
            'first_name': user.first_name, 'second_name': user.second_name,
            'login': user.login
            }
        access_token = create_access_token(identity=body['email'],
                                           additional_claims=claims)
        refresh_token = create_refresh_token(identity=body['email'],
                                             additional_claims=claims)
        return ({'access_token': access_token, 'refresh_token': refresh_token},
                HTTPStatus.OK)
    else:
        return 'Wrong password', HTTPStatus.BAD_REQUEST


@jwt_required(refresh=True)
def refresh_token() -> tuple[dict, HTTPStatus]:
    """Функция обновления access-токена"""
    current_user = get_jwt_identity()
    user = db.session.query(User).filter(User.email == current_user).first()
    claims = {
            'first_name': user.first_name, 'second_name': user.second_name,
            'login': user.login
            }
    access_token = create_access_token(identity=current_user,
                                       additional_claims=claims)
    return {'access_token': access_token}, HTTPStatus.OK


@jwt_required()
def logout() -> tuple[str, HTTPStatus]:
    """Функция выхода из аккаунта (удаление access-tokena)"""
    jti = get_jwt()['jti']
    revoked_token = RevokedTokenModel(jti=jti)
    revoked_token.add()
    return 'Access token has been revoked', HTTPStatus.OK


@jwt_required(refresh=True)
def logout_refresh() -> tuple[str, HTTPStatus]:
    """Удаление refresh-токена"""
    jti = get_jwt()['jti']
    revoked_token = RevokedTokenModel(jti=jti)
    revoked_token.add()
    return 'Refresh token has been revoked', HTTPStatus.OK


@jwt_required()
def index() -> tuple[str, HTTPStatus]:
    """Тестовая функция"""
    current_user = get_jwt_identity()
    return f'Hello, {current_user}', HTTPStatus.OK
