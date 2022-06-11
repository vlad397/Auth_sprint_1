import typer
from flask_migrate import init, migrate, upgrade
from gevent.pywsgi import WSGIServer
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from config import app, db
from db.db_models import Role, RolesUsers, SocialNetwork, User
from settings import Settings

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

typer_app = typer.Typer()


@typer_app.command()
def runserver():
    """Runs a server"""
    http_server = WSGIServer(
        (settings.wsgi_host, settings.wsgi_port), app, spawn=settings.workers
    )
    http_server.serve_forever()


@typer_app.command()
def createsuperadmin(email: str, login: str, password: str) -> None:
    """Creates superadmin, requires email and password"""
    try:
        user = User(
                first_name='superadmin', second_name='superadmin',
                login=login, email=email,
                password=generate_password_hash(password)
            )
        db.session.add(user)
        db.session.commit()

        role_for_user = Role.query.filter_by(name='superadmin').first()
        if not role_for_user:
            role = Role(name='superadmin', description='God')
            db.session.add(role)
            db.session.commit()
            role_for_user = Role.query.filter_by(name='superadmin').first()

        user_for_role = User.query.filter_by(email=email).first()

        role_user = RolesUsers(
            user_id=user_for_role.id, role_id=role_for_user.id)
        db.session.add(role_user)
        db.session.commit()

        print('Created')

    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            print('User already exists')


@typer_app.command()
def createbasics():
    """Creates basic social networks"""
    try:
        s_n_1 = SocialNetwork(name='google')
        s_n_2 = SocialNetwork(name='yandex')
        s_n_3 = SocialNetwork(name='vk')

        db.session.add(s_n_1)
        db.session.add(s_n_2)
        db.session.add(s_n_3)
        db.session.commit()

        print('Created')

    except IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            print('Social Networks already exist')


@typer_app.command()
def dbmigrate(message=None):
    migrate(message=message)


@typer_app.command()
def dbupgrade(message=None):
    upgrade()


@typer_app.command()
def dbinit(message=None):
    init()
