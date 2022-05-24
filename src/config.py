import connexion
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

from db.db import db, init_db
from db.db_models import (BasicRoleEnum, RevokedTokenModel, Role, RolesUsers,
                          User)
from settings import Settings


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')


connex_app = connexion.App(__name__,
                           specification_dir='../openapi/', server='gevent')
app = connex_app.app

app.secret_key = settings.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{settings.pg_user}:'
                                         f'{settings.pg_password}@'
                                         f'{settings.host}/{settings.pg_db}')
app.config['JWT_SECRET_KEY'] = settings.jwt_secret_key

jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return RevokedTokenModel.is_jti_blocklisted(jti)


init_db(app)
app.app_context().push()
db.create_all()

user = User(
            first_name='super', second_name='user',
            login='superuser', email='superuser@gmail.com',
            password=generate_password_hash('admin'),
            role=BasicRoleEnum.superadmin
        )
try:
    db.session.add(user)
    db.session.commit()
except:
    pass
