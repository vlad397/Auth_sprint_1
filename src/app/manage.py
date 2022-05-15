import connexion

app = connexion.FlaskApp(__name__, specification_dir='', server='gevent')
app.add_api('')
app.run(port=8000)