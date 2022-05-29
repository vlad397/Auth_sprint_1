import re
from datetime import datetime
from http import HTTPStatus

from flask import request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required,
                                verify_jwt_in_request)
from jsonschema import draft4_format_checker
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from db.db import db
from db.db_models import AuthHistory, RevokedTokenModel, User
from app.response_messages import ReqMessage


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
        return ReqMessage.SUCCESS_REG, HTTPStatus.CREATED

    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            return ReqMessage.USER_EXIST, HTTPStatus.BAD_REQUEST
        else:
            return ReqMessage.UNEXPECTED_ERROR, HTTPStatus.BAD_REQUEST


def login(body: dict) -> tuple[str | dict, HTTPStatus]:
    """Функция входа в аккаунт"""
    current_token = verify_jwt_in_request(optional=True)

    # Если в заголовке уже есть токен, то вход не нужен
    if current_token:
        return ReqMessage.ALREADY_LOGIN, HTTPStatus.NOT_ACCEPTABLE

    user = User.query.filter_by(email=body['email']).first()
    if not user:
        return ReqMessage.NOT_EXIST_USER, HTTPStatus.NOT_FOUND

    if check_password_hash(user.password, body['password']):
        # TODO: request.user_agent не работает в новых версиях flask, werkzeug
        agent = request.user_agent

        auth = AuthHistory(user_id=user.id, browser=agent.browser,
                           platform=agent.platform, timestamp=datetime.now())
        db.session.add(auth)
        db.session.commit()

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
    return ReqMessage.WRONG_PASSWORD, HTTPStatus.BAD_REQUEST


@jwt_required(refresh=True)
def refresh_token() -> tuple[dict, HTTPStatus]:
    """Функция обновления access-токена"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

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
    return ReqMessage.LOGOUT_ACCESS, HTTPStatus.OK


@jwt_required(refresh=True)
def logout_refresh() -> tuple[str, HTTPStatus]:
    """Удаление refresh-токена"""
    jti = get_jwt()['jti']
    revoked_token = RevokedTokenModel(jti=jti)
    revoked_token.add()
    return ReqMessage.LOGOUT_REFRESH, HTTPStatus.OK


@jwt_required()
def get_history(page: int = 1, count: int = 50) -> tuple[dict, HTTPStatus]:
    """История входа в аккаунт"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    history = db.session.query(
        AuthHistory).filter(AuthHistory.user_id == user.id).paginate(page=page, per_page=count, error_out=False).items

    return {'history': f'{history}'}, HTTPStatus.OK


@jwt_required()
def change_login(body) -> tuple[str, HTTPStatus]:
    """Изменение логина пользователя"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    if check_password_hash(user.password, body['password']):
        try:
            user.login = body['login']
            db.session.commit()
            return ReqMessage.SUCCESS_LOGIN_CHANGE, HTTPStatus.OK

        except IntegrityError as err:
            if isinstance(err.orig, UniqueViolation):
                return (ReqMessage.USER_EXIST,
                        HTTPStatus.BAD_REQUEST)

    return ReqMessage.WRONG_PASSWORD, HTTPStatus.BAD_REQUEST


@jwt_required()
def change_password(body) -> tuple[str, HTTPStatus]:
    """Изменение пароля пользователя"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    if check_password_hash(user.password, body['old_password']):
        user.password = generate_password_hash(body['new_password'])
        db.session.commit()
        return ReqMessage.SUCCESS_PASS_CHANGE, HTTPStatus.OK

    return ReqMessage.WRONG_PASSWORD, HTTPStatus.BAD_REQUEST
