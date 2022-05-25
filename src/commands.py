import click
from flask import Blueprint
from .db.db_models import (BasicRoleEnum, User, Role, RolesUsers)
from .config import db
from werkzeug.security import generate_password_hash
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError


usersbp = Blueprint('users', __name__)

@usersbp.cli.command('create_super_admin')
@click.argument('email')
@click.argument('password')
def create(email, password):
    """ Creates superadmin, requires email and password"""
    try:
        user = User(
                first_name='superadmin', second_name='superadmin',
                login='superadmin', email=email,
                password=generate_password_hash(password),
                role=BasicRoleEnum.superadmin
            )
        db.session.add(user)
        db.session.commit()

        role = Role(name='superadmin', description='God')
        db.session.add(role)
        db.session.commit()

        role_for_user = db.session.query(Role).filter(Role.name == 'superadmin').first()
        user_for_role = db.session.query(User).filter(User.email == email).first()

        role_user = RolesUsers(user_id=user_for_role.id, role_id=role_for_user.id)
        db.session.add(role_user)
        db.session.commit()

        print('Created')

    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            print('User already exists')