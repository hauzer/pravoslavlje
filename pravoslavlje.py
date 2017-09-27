from itertools import groupby

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


jinja_vars = {}


def add_as_jinja_var(func):
    jinja_vars[func.__name__] = func
    return func


def render_template(*args, **kwargs):
    return flask.render_template(*args, **combine_dicts(jinja_vars, kwargs))


@add_as_jinja_var
def url_for_static(filename, *args, **kwargs):
    return url_for('static', *args, filename=filename, **kwargs)


def attach_method(obj, attr):
    def decorator(func):
        setattr(obj, attr, func)
        return func

    return decorator


@attach_method(db.Issue, 'url')
@property
def issue_url(self):
    return url_for('issue', number=self.number)


@attach_method(db.Issue, 'pdf_url')
@property
def issue_pdf_url(self):
    return url_for_static(self.pdf_path)


@attach_method(db.Issue, 'cover_url')
@property
def issue_cover_url(self):
    return url_for_static(self.cover_path)


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


tabs = {
    'new_issue':       'Нови број',
    'archive':         'Архива',
    'subscription':    'Претплата',
    'about':           'О новинама',
    # 'contact':         'Контакт',
}
jinja_vars['tabs'] = tabs


@app.route('/')
def index():
    return new_issue()


@app.route('/архива')
def archive():
    g.issues = []
    issues = db.session.query(db.Issue).order_by(sql.desc(db.Issue.date))
    for year, year_issues in groupby(issues, lambda i: i.date.year):
        g.issues.append((year, []))
        for month, month_issues in \
                groupby(year_issues, lambda i: i.date.month):
            list_month_issues = list(month_issues)
            g.issues[-1][1].append((
                list_month_issues[0].month_name,
                list_month_issues
            ))

    return render_template('archive.html')


@app.route('/нови-број')
def new_issue():
    issue = db.session.query(db.Issue) \
        .order_by(sql.desc(db.Issue.date)).first()
    return redirect(url_for('issue', number=issue.number))


@app.route('/претплата')
def subscription():
    return render_template('subscription.html')


@app.route('/о-новинама')
def about():
    return render_template('about.html')


@app.route('/контакт')
def contact():
    return render_template('contact.html')


@app.route('/број/<number>')
def issue(number):
    g.issue = db.session.query(db.Issue) \
        .filter(db.Issue.number == number).first()

    if g.issue:
        newest_issue = db.session.query(db.Issue) \
            .order_by(sql.desc(db.Issue.date)).first()
        if g.issue == newest_issue:
            current_tab = 'new_issue'
        return render_template('issue.html', current_tab=current_tab)
    else:
        return abort(404)
