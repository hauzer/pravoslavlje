from itertools import groupby
from babel.dates import get_month_names

import flask
from flask import Flask, abort, g, redirect, request, session, url_for
from flask_session import Session
from flask_profile import Profiler

import db
import sqlalchemy as sql


def combine_dicts(*dicts):
    keys_values = []
    for dct in dicts:
        if dct:
            keys_values.extend(list(dct.items()))
    return dict(keys_values)


def attach_method(obj, attr):
    def decorator(func):
        setattr(obj, attr, func)
        return func

    return decorator


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


@app.route('/уредништво')
def editorial_board():
    return render_template('editorial_board.html')


@app.route('/нови-број')
def new_issue():
    return render_template('new_issue.html')


@app.route('/архива')
def archive():
    g.issues = []
    issues = db.session.query(db.Issue).order_by(sql.desc(db.Issue.date))
    for year, year_issues in groupby(issues, lambda i: i.date.year):
        g.issues.append((year, []))
        for month, month_issues in \
                groupby(year_issues, lambda i: i.date.month):
            g.issues[-1][1].append((
                get_month_names(width='wide', locale='sr')[month],
                list(month_issues)
            ))

    return render_template('archive.html')


@app.route('/претплата')
def subscription():
    return render_template('subscription.html')


@app.route('/сарадници')
def associates():
    return render_template('associates.html')


@app.route('/о-новинама')
def about():
    return render_template('about.html')


@app.route('/контакт')
def contact():
    return render_template('contact.html')


@app.route('/број/<number>')
def issue(number):
    g.issue = \
        db.session.query(db.Issue).filter(db.Issue.number == number).first()

    if g.issue:
        return render_template('issue.html')
    else:
        return abort(404)
