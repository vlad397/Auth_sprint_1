from http import HTTPStatus

from flask_jwt_extended import (get_jwt_identity, jwt_required)
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from db.db import db
from db.db_models import Role, RolesUsers, User

from .permissions import admin_affects_on_superadmin, is_admin, is_super_admin


@jwt_required()
def create_role(body: dict) -> tuple[str, HTTPStatus]:
    """Создание роли"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    # Если пользователь не админ/суперадмин - отказ
    if not is_admin(user) and not is_super_admin(user):
        return 'You do not have rights', HTTPStatus.FORBIDDEN

    role = Role(name=body['name'], description=body['description'])

    try:
        db.session.add(role)
        db.session.commit()
        return 'Role created', HTTPStatus.CREATED
    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            return 'Role already exists', HTTPStatus.BAD_REQUEST
        else:
            return 'Unexpected error', HTTPStatus.BAD_REQUEST


@jwt_required()
def change_role(role_id: str, body: dict) -> tuple[str, HTTPStatus]:
    """Изменение роли"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    # Если пользователь не админ/суперадмин - отказ
    if not is_admin(user) and not is_super_admin(user):
        return 'You do not have rights', HTTPStatus.FORBIDDEN

    role = Role.query.filter_by(id=role_id).first()

    if role:
        # Если пытаются изменить защищенные роли - отказ
        if role in Role.Meta.PROTECTED_ROLE_NAMES:
            return 'Cannot change this role', HTTPStatus.BAD_REQUEST

        try:
            role.name = body['name']
            role.description = body['description']
            db.session.commit()
        except IntegrityError as err:
            if isinstance(err.orig, UniqueViolation):
                return 'Role already exists', HTTPStatus.BAD_REQUEST
        return 'Role changed', HTTPStatus.OK

    return 'No such role', HTTPStatus.NOT_FOUND


@jwt_required()
def delete_role(role_id: str) -> tuple[str, HTTPStatus]:
    """Удаление роли"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    # Если пользователь не админ/суперадмин - отказ
    if not is_admin(user) and not is_super_admin(user):
        return 'You do not have rights', HTTPStatus.FORBIDDEN

    role = Role.query.filter_by(id=role_id).first()

    if role:
        # Если пытаются удалить защищенные роли - отказ
        if role in Role.Meta.PROTECTED_ROLE_NAMES:
            return 'Cannot delete this role', HTTPStatus.BAD_REQUEST

        db.session.delete(role)
        db.session.commit()
        return 'Role deleted', HTTPStatus.OK

    return 'No such role', HTTPStatus.NOT_FOUND


@jwt_required()
def give_role(user_id: str, role_id: str) -> tuple[str, HTTPStatus]:
    """Назначение роли пользователю"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    # Если пользователь не админ/суперадмин - отказ
    if not is_admin(user) and not is_super_admin(user):
        return 'You do not have rights', HTTPStatus.FORBIDDEN

    request_user = User.query.filter_by(id=user_id).first()
    role = Role.query.filter_by(id=role_id).first()

    # Если админ пытается дать роль суперадмину - отказ
    if admin_affects_on_superadmin(user, request_user):
        return 'You do not have rights', HTTPStatus.FORBIDDEN

    if request_user and role:
        user_role = RolesUsers(user_id=user_id, role_id=role_id)

        try:
            db.session.add(user_role)
            db.session.commit()
        except IntegrityError as err:
            if isinstance(err.orig, UniqueViolation):
                return 'User already has this role', HTTPStatus.BAD_REQUEST

        return 'Role is given', HTTPStatus.CREATED

    return 'No such role or user', HTTPStatus.NOT_FOUND


@jwt_required()
def take_role(user_id: str, role_id: str) -> tuple[str, HTTPStatus]:
    """Удаление роли пользователя"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    # Если пользователь не админ/суперадмин - отказ
    if not is_admin(user) and not is_super_admin(user):
        return 'You do not have rights', HTTPStatus.FORBIDDEN

    request_user = User.query.filter_by(id=user_id).first()

    # Если админ пытается забрать роль суперадмина - отказ
    if admin_affects_on_superadmin(user, request_user):
        return 'You do not have rights', HTTPStatus.FORBIDDEN

    user_role = RolesUsers.query.filter_by(
        user_id=user_id, role_id=role_id).first()

    if user_role:
        db.session.delete(user_role)
        db.session.commit()
        return 'Role was taken', HTTPStatus.OK
    return 'No such role or user', HTTPStatus.BAD_REQUEST
