import connexion
import ssl
from db.db import init_db
from settings import Settings

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

# Ниже попытка подрубить https, пока без успеха
'''
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('./src/keys/key.pem')
context.use_certificate_file('./src/keys/cert.pem')
'''
'''
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain('./src/keys/cert.pem', './src/keys/key.pem')
'''
app = connexion.FlaskApp(__name__, specification_dir='../openapi/', server='gevent')
app.add_api('auth.yaml', strict_validation=True)


if __name__ == '__main__':
    init_db()
    app.run(host=settings.host, port=settings.port, debug=True)
