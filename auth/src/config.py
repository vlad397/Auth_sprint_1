import os
from http import HTTPStatus

import connexion
from authlib.integrations.flask_client import OAuth
from flask import Flask, jsonify, make_response, request
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider        
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from db.db import db, init_db
from db.db_models import RevokedTokenModel
from settings import Settings

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

connex_app = connexion.App(__name__,
                           specification_dir='../openapi/', server='gevent')
connex_app.add_api('auth.yaml', strict_validation=True)

app: Flask = connex_app.app

app.secret_key = settings.secret_key
app.config['JWT_SECRET_KEY'] = settings.jwt_secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{settings.pg_user}:'
                                         f'{settings.pg_password}@'
                                         f'{settings.host}:f{settings.port}/{settings.pg_db}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RATELIMIT_STORAGE_URI'] = (f'redis://{settings.redis_host}:'
                                       f'{settings.redis_port}')

@app.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is required')   


init_db(app)
app.app_context().push()
db.create_all()

def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name='localhost',
                agent_port=6831,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

configure_tracer()


FlaskInstrumentor().instrument_app(app) 


MIGRATION_DIR = os.path.join('src/db', 'migrations')

migrate = Migrate(app, db, directory=MIGRATION_DIR)

limiter = Limiter(app, key_func=get_remote_address,
                  default_limits=['20/minute'])
limiter.init_app(app)

jwt = JWTManager(app)


oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=settings.client_id_google,
    client_secret=settings.client_secret_google,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)


def yandex_compliance_fix(client, user_data):
    return {
        'login': user_data['login'],
        'email': user_data['default_email'],
        'given_name': user_data['first_name'],
        'family_name': user_data['last_name'],
    }


yandex = oauth.register(
    name='yandex',
    authorize_params={'response_type': 'code', },
    client_id=settings.client_id_yandex,
    client_secret=settings.client_secret_yandex,
    userinfo_endpoint='https://login.yandex.ru/info',
    token_placement='header',
    userinfo_compliance_fix=yandex_compliance_fix,
    access_token_url='https://oauth.yandex.ru/token',
    authorize_url='https://oauth.yandex.ru/authorize',
    api_base_url='https://oauth.yandex.ru',
)


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return RevokedTokenModel.is_jti_blocklisted(jti)


@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(
        jsonify(error='Too many requests'), HTTPStatus.TOO_MANY_REQUESTS)
