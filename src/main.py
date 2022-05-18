import config

connex_app = config.connex_app
connex_app.add_api('auth.yaml', strict_validation=True)

if __name__ == '__main__':
    connex_app.run(debug=True)


# Ниже попытка подрубить https, пока без успеха
'''
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('./src/keys/cert.pem', './src/keys/key.pem')
'''
