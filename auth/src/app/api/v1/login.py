from http import HTTPStatus

from flask import request, url_for
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required,
                                verify_jwt_in_request)
from werkzeug.security import check_password_hash
from werkzeug.wrappers.response import Response

import config
from app.response_messages import ReqMessage
from db.db import db
from db.db_models import RevokedTokenModel, SocialNetwork, SocialUser, User

from .basics import (add_auth_history, basic_oauth_link_authorization,
                     basic_oauth_login_authorization)


def login(body: dict) -> tuple[str | dict, HTTPStatus]:
    """Функция входа в аккаунт"""
    current_token = verify_jwt_in_request(optional=True)

    # Если в заголовке уже есть токен, то вход не нужен
    if current_token:
        return ReqMessage.ALREADY_LOGIN, HTTPStatus.ACCEPTED

    user = User.query.filter_by(email=body['email']).first()
    if not user:
        return ReqMessage.NOT_EXIST_USER, HTTPStatus.NOT_FOUND

    if not user.password:
        return ReqMessage.NOT_EXIST_USER, HTTPStatus.NOT_FOUND

    if check_password_hash(user.password, body['password']):
        # TODO: request.user_agent не работает в новых версиях flask, werkzeug
        add_auth_history(user, request)

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


def login_oauth(provider: str) -> Response | tuple[str, HTTPStatus]:
    """Функция для входа через OAuth Google,
    перенаправляет в login_authorize_google для авторизации через Google"""

    # Если указана несуществующая соц сеть - ошибка
    if provider not in ['google', 'yandex']:
        return 'Social network not found', HTTPStatus.BAD_REQUEST

    social = config.oauth.create_client(provider)
    redirect_uri = url_for(
        f'/api/v1.app_api_v1_login_login_authorize_{provider}',
        _external=True
    )
    return social.authorize_redirect(redirect_uri)


def login_authorize_google() -> tuple[str | dict, HTTPStatus]:
    """Функция для входа через OAuth Google"""
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

    return basic_oauth_login_authorization(user, 'google')


def login_authorize_yandex() -> tuple[str | dict, HTTPStatus]:
    """Функция для входа через OAuth Google"""
    yandex = config.oauth.create_client('yandex')
    token = yandex.authorize_access_token()
    user = yandex.get('userinfo', token=token)

    # Если после авторизации в яндексе информация пустая - пробуем иначе
    if not user:
        user = dict(config.oauth.yandex.userinfo())

    # Если все равно нет информации - ошибка
    if not user:
        return ReqMessage.SOMETHING_WENT_WRONG, HTTPStatus.BAD_REQUEST

    return basic_oauth_login_authorization(user, 'yandex')


@jwt_required()
def unlink(provider: str):
    """Функция отвязывания аккаунта"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    # Для отвязывания соц сети обязательно нужно создать пароль,
    # чтобы человек мог входить в стандартный аккаунт после отвязки
    if user.password is None:
        return ReqMessage.NEED_PASSWORD, HTTPStatus.BAD_REQUEST

    # Если соц сеть не привязана - ошибка
    if provider not in user.social_list():
        return (ReqMessage.PROVIDER_NOT_LINKED.format(provider),
                HTTPStatus.NOT_FOUND)

    social = SocialNetwork.query.filter_by(name=provider).first()
    social_user = SocialUser.query.filter_by(
        user_id=user.id, social_id=social.id
    ).first()

    db.session.delete(social_user)
    db.session.commit()

    return ReqMessage.PROVIDER_UNLINKED.format(provider), HTTPStatus.OK


@jwt_required()
def link(provider: str):
    """Функция привязывания аккаунта"""

    # Если указана несуществующая соц сеть - ошибка
    if provider not in ['google', 'yandex']:
        return ReqMessage.SOCIAL_NOT_FOUND, HTTPStatus.BAD_REQUEST

    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    # Вероятнее всего, человек отвязал соц сеть и решил привязать новую,
    # а значит он должен был создать пароль, убедимся в этом. В целом, лучше
    # иметь возможность входить в аккаунт прежде, чем привязывать и отвязывать
    if user.password is None:
        return ReqMessage.NEED_PASSWORD, HTTPStatus.BAD_REQUEST

    social = SocialNetwork.query.filter_by(name=provider).first()
    social_user = SocialUser.query.filter_by(
        user_id=user.id, social_id=social.id
    ).first()

    # Если соц сеть уже привязана - ошибка
    if social_user is not None:
        return (ReqMessage.PROVIDER_ALREADY_LINKED.format(provider),
                HTTPStatus.BAD_REQUEST)

    provider_network = config.oauth.create_client(provider)
    redirect_uri = url_for(
        f'/api/v1.app_api_v1_login_link_authorize_{provider}',
        _external=True
    )
    return provider_network.authorize_redirect(redirect_uri)


@jwt_required()
def link_authorize_google():
    google = config.oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo', token=token)

    # Если после авторизации в гугле информация пустая - ошибка
    if not resp:
        return ReqMessage.SOMETHING_WENT_WRONG, HTTPStatus.BAD_REQUEST

    user = get_jwt_identity()

    return basic_oauth_link_authorization(user, 'google')


@jwt_required()
def link_authorize_yandex():
    yandex = config.oauth.create_client('yandex')
    token = yandex.authorize_access_token()
    resp = yandex.get('userinfo', token=token)

    # Если после авторизации в яндексе информация пустая - пробуем иначе
    if not resp:
        resp = dict(config.oauth.yandex.userinfo())

    # Если все равно нет информации - ошибка
    if not resp:
        return ReqMessage.SOMETHING_WENT_WRONG, HTTPStatus.BAD_REQUEST

    user = get_jwt_identity()

    return basic_oauth_link_authorization(user, 'yandex')
