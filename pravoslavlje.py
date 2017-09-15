import flask
from flask import Flask, abort, g, redirect, request, session, url_for
from flask_session import Session
from flask_profile import Profiler

import db


def combine_dicts(*dicts):
    keys_values = []
    for dct in dicts:
        if dct:
            keys_values.extend(list(dct.items()))
    return dict(keys_values)


jinja_exports = {}


def export_to_jinja(func):
    jinja_exports[func.__name__] = func
    return func


def render_template(*args, **kwargs):
    return flask.render_template(*args, **combine_dicts(jinja_exports, kwargs))


@export_to_jinja
def url_for_static(filename, *args, **kwargs):
    return url_for('static', *args, filename=filename, **kwargs)


tabs = {
    'editorial_board': 'Уредништво',
    'new_issue':       'Нови број',
    'archive':         'Архива',
    'subscription':    'Претплата',
    'associates':      'Сарадници',
    'about':           'О новинама',
    'contact':         'Контакт',
}
jinja_exports['tabs'] = tabs

# FIXME: files 404ing in the root static directory
app = Flask(__name__, static_path='/files')
app.config.from_object(__name__)
app.config.update({
    'SECRET_KEY':       '!!!!!!! TEST KEY CHANGE ME !!!!!!!!',
    'SESSION_TYPE':     'filesystem',
    'SESSION_FILE_DIR': 'sessions'
})
app.config.from_envvar('PRAVOSLAVLJE_SETTINGS', silent=True)

Profiler(app)
Session(app)


@app.teardown_appcontext
def remove_db_session(exception=None):
    db.session.remove()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urednistvo')
def editorial_board():
    return render_template('editorial_board.html')


@app.route('/novi-broj')
def new_issue():
    return render_template('new_issue.html')


@app.route('/arhiva')
def archive():
    return render_template('archive.html')


@app.route('/pretplata')
def subscription():
    return render_template('subscription.html')


@app.route('/saradnici')
def associates():
    return render_template('associates.html')


@app.route('/o-novinama')
def about():
    return render_template('about.html')


@app.route('/kontakt')
def contact():
    return render_template('contact.html')
