import os

import connexion
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db.db import db, init_db
from db.db_models import RevokedTokenModel
from settings import Settings

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

connex_app = connexion.App(__name__,
                           specification_dir='../openapi/', server='gevent')
connex_app.add_api('auth.yaml', strict_validation=True)

app = connex_app.app

app.secret_key = settings.secret_key
app.config['JWT_SECRET_KEY'] = settings.jwt_secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{settings.pg_user}:'
                                         f'{settings.pg_password}@'
                                         f'{settings.host}/{settings.pg_db}')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


init_db(app)
app.app_context().push()
db.create_all()

MIGRATION_DIR = os.path.join('src/db', 'migrations')

migrate = Migrate(app, db, directory=MIGRATION_DIR)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return RevokedTokenModel.is_jti_blocklisted(jti)
