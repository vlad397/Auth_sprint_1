from datetime import datetime
from http import HTTPStatus

from authlib.oidc.core.claims import UserInfo
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.local import LocalProxy

import config
from app.response_messages import ReqMessage
from db.db import db
from db.db_models import (AuthHistory, BasicSocialEnum, SocialNetwork,
                          SocialUser, User)


def add_auth_history(user: User, request: LocalProxy) -> None:
    """Функция записи входа в аккаунт"""
    agent = request.user_agent

    auth = AuthHistory(user_id=user.id, browser=agent.browser,
                       platform=agent.platform, timestamp=datetime.now())

    db.session.add(auth)
    db.session.commit()


def basic_oauth_register_authorization(
    user: UserInfo | dict, provider: str
) -> tuple[str | dict, HTTPStatus]:
    """Базовая функция авторизации в соц сети для регистрации"""

    # Если пользователя в системе нет - регистрируем
    if not db.session.query(
        db.exists().where(User.email == user['email'])
    ).scalar():
        user_to_register = User(
            first_name=user['given_name'], second_name=user['family_name'],
            login=user['email'], email=user['email'],
            password=None)
        db.session.add(user_to_register)

        # Создаем связь аккаунта и соц сети
        user_for_social = User.query.filter_by(email=user['email']).first()
        social = SocialNetwork.query.filter_by(name=provider).first()
        social_user = SocialUser(
            user_id=user_for_social.id, social_id=social.id
        )

        db.session.add(social_user)
        db.session.commit()

        # Регистрация была через соц сеть - выдаем токен без входа в аккаунт
        claims = {
            'first_name': user['given_name'],
            'second_name': user['family_name'],
            'login': user['email']
        }

        access_token = create_access_token(identity=user['email'],
                                           additional_claims=claims)
        refresh_token = create_refresh_token(identity=user['email'],
                                             additional_claims=claims)

        # Добавляем запись о входе в аккаунт
        add_auth_history(user_for_social, request)

        return ({
            'message': 'Registered successfully',
            'access_token': access_token,
            'refresh_token': refresh_token
            }, HTTPStatus.CREATED)
    return ('User already exists', HTTPStatus.BAD_REQUEST)


def basic_oauth_link_authorization(
    current_user: str, provider: str
) -> tuple[str | dict, HTTPStatus]:
    """Базовая функция авторизации в соц сети для привязки соц сети"""

    # Берем пользователя и указанную соц сеть
    user = User.query.filter_by(email=current_user).first()
    social = SocialNetwork.query.filter_by(name=provider).first()

    # Создаем связь пользователя и соц сети
    social_user_new = SocialUser(user_id=user.id, social_id=social.id)

    db.session.add(social_user_new)
    db.session.commit()

    return f'{provider} linked', HTTPStatus.OK


def basic_oauth_login_authorization(
    user: UserInfo | dict, provider: str
) -> tuple[str | dict, HTTPStatus]:
    """Базовая функция авторизации в соц сети для входа в аккаунт"""
    # Ищем пользователя в базе
    if not db.session.query(
        db.exists().where(User.email == user['email'])
    ).scalar():
        return ReqMessage.NOT_EXIST_USER, HTTPStatus.NOT_FOUND

    current_user = User.query.filter_by(email=user['email']).first()

    # Если соц сеть не привязана - ошибка
    if provider not in current_user.social_list():
        return (ReqMessage.PROVIDER_NOT_LINKED.format(provider),
                HTTPStatus.BAD_REQUEST)

    # Добавляем запись о входе в аккаунт
    add_auth_history(current_user, request)

    claims = {
        'first_name': user['given_name'], 'second_name': user['family_name'],
        'login': user['email']
        }

    access_token = create_access_token(identity=user['email'],
                                       additional_claims=claims)
    refresh_token = create_refresh_token(identity=user['email'],
                                         additional_claims=claims)

    return ({
        'message': 'Logged in successfully',
        'access_token': access_token,
        'refresh_token': refresh_token
        }, HTTPStatus.CREATED)


def basic_authorize_google() -> UserInfo:
    """Базовая функция для получения информации о пользователе"""
    google = config.oauth.create_client(BasicSocialEnum.google.value)
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)
    user = resp.json()

    #  Если после авторизации в гугле информация пустая - пробуем иначе
    if not user:
        user = config.oauth.google.userinfo()

    return user


def basic_authorize_yandex() -> UserInfo | dict:
    """Базовая функция для получения информации о пользователе"""
    yandex = config.oauth.create_client(BasicSocialEnum.yandex.value)
    token = yandex.authorize_access_token()
    user = yandex.get('userinfo', token=token)

    # Если после авторизации в яндексе информация пустая - пробуем иначе
    if not user:
        user = dict(config.oauth.yandex.userinfo())

    return user
