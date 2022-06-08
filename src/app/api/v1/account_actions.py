from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity, jwt_required
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.response_messages import ReqMessage
from db.db import db
from db.db_models import AuthHistory, User


@jwt_required()
def get_history(page: int = 1, count: int = 50) -> tuple[dict, HTTPStatus]:
    """История входа в аккаунт"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    history = db.session.query(
        AuthHistory).filter(
            AuthHistory.user_id == user.id).paginate(
                page=page, per_page=count, error_out=False).items

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


@jwt_required()
def create_password(body) -> tuple[str, HTTPStatus]:
    """Создание пароля пользователя"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    if user.password is not None:
        return 'You already have password', HTTPStatus.BAD_REQUEST

    user.password = generate_password_hash(body['new_password'])
    db.session.commit()

    return ReqMessage.SUCCESS_PASS_CREATE, HTTPStatus.OK
