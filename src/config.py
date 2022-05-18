from datetime import timedelta

import connexion
from authlib.integrations.flask_client import OAuth

from db.db import db, init_db
from settings import Settings


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')


connex_app = connexion.App(__name__,
                           specification_dir='../openapi/', server='gevent')
app = connex_app.app

app.secret_key = settings.secret_key
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)
app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{settings.pg_user}:'
                                         f'{settings.pg_password}@'
                                         f'{settings.host}/{settings.pg_db}')

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=settings.client_id,
    client_secret=settings.client_secret,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

init_db(app)
app.app_context().push()
db.create_all()
