from flask import Flask, g, request, url_for
from flask_session import Session
from flask_profile import Profiler


class Config:
    DEBUG = True
    SECRET_KEY = 'head -c 32 /dev/random | base64'
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'sessions'


app = Flask(__name__)
app.config.from_object(Config)
app.config.from_envvar('PRAVOSLAVLJE_SETTINGS', silent=True)

Profiler(app)
Session(app)


@app.template_global()
def url_for_static(filename, *args, **kwargs):
    return url_for('static', *args, filename=filename, **kwargs)


@app.before_request
def set_endpoint():
    g.endpoint = request.endpoint
