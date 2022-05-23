from http import HTTPStatus

from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from db.db import db
from db.db_models import Role, RolesUsers, User


def create_role(body: dict) -> tuple[str, HTTPStatus]:
    """Создание роли"""
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


def change_role(role_id: str, body: dict) -> tuple[str, HTTPStatus]:
    """Изменение роли"""
    role = db.session.query(Role).filter(Role.id == role_id).first()
    if role:
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


def delete_role(role_id: str) -> tuple[str, HTTPStatus]:
    """Удаление роли"""
    role = db.session.query(Role).filter(Role.id == role_id).first()
    if role:
        if role in Role.Meta.PROTECTED_ROLE_NAMES:
            return 'Cannot delete this role', HTTPStatus.BAD_REQUEST
        db.session.delete(role)
        db.session.commit()
        return 'Role deleted', HTTPStatus.OK
    return 'No such role', HTTPStatus.NOT_FOUND


def give_role(user_id: str, role_id: str) -> tuple[str, HTTPStatus]:
    """Назначение роли пользователю"""
    user = db.session.query(User).filter(User.id == user_id).first()
    role = db.session.query(Role).filter(Role.id == role_id).first()
    if user and role:
        user_role = RolesUsers(user_id=user_id, role_id=role_id)
        try:
            db.session.add(user_role)
            db.session.commit()
        except IntegrityError as err:
            if isinstance(err.orig, UniqueViolation):
                return 'User already has this role', HTTPStatus.BAD_REQUEST
        return 'Role is given', HTTPStatus.CREATED
    return 'No such role or user', HTTPStatus.NOT_FOUND


def take_role(user_id: str, role_id: str) -> tuple[str, HTTPStatus]:
    """Удаление роли пользователя"""
    user_role = db.session.query(RolesUsers).filter(
        user_id == user_id, role_id == role_id
    ).first()
    if user_role:
        db.session.delete(user_role)
        db.session.commit()
        return 'Role was taken', HTTPStatus.OK
    return 'No such role or user', HTTPStatus.BAD_REQUEST
