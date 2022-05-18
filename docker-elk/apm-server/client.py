import elasticapm
from elasticapm.contrib.flask import ElasticAPM

from flask import Flask

app = Flask(__name__)

app.config['ELASTIC_APM'] = {
    # Set required service name. Allowed characters:
    # a-z, A-Z, 0-9, -, _, and space
    'APP_NAME': 'flask-apm-client',
    # Use if APM Server requires a token
    'SECRET_TOKEN': '',
    'SERVICE_NAME': 'PYTHON_FLASK_TEST_APP',
    'SERVER_URL': 'http://YOUR_IP:8200',
    'DEBUG': True,
}

apm = ElasticAPM(app)

@app.route('/test')
def test():
    return "test"

@app.route('/slow')
def slow():
    import time
    time.sleep(5)
    return "slow"

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
