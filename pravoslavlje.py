from bidict import bidict
from functools import wraps
from itertools import groupby
import os

import sqlite3

from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from flask_babelex import lazy_gettext as _, Babel, Locale
from flask_session import Session
from flask_profile import Profiler


def get_db():
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect(
            'db.sqlite3',
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    results = getattr(cur, {True: 'fetchone', False: 'fetchall'}[one])()
    cur.close()

    if results is not None:
        return results[0] if one else results


def generate_db_issues_from_pdfs(year, month, day):
    with app.app_context():
        query_db('DELETE FROM issues')
        for pdf in sorted(os.listdir('static/pdfs')):
            number = pdf.split('.')[0]
            date = '{}-{:02}-{:02}'.format(year, month, day)
            query_db('INSERT INTO issues (number, date) VALUES (?, ?)', (number, date))

            if day == 15 and month == 12:
                year += 1

            if month == 1 or month == 8:
                day = 1
                month += 1
            else:
                if day == 15:
                    if month == 12:
                        month = 1
                    else:
                        month += 1

                if day == 1:
                    day = 15
                else:
                    day = 1

        get_db().commit()


def init_db():
    with app.app_context():
        db = get_db()
        schema = open('db.schema', 'r')
        cur = db.cursor()
        cur.executescript(schema.read())
        schema.close()
        cur.close()
        db.commit()


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update({
    'SESSION_TYPE':     'filesystem',
    'SESSION_FILE_DIR': 'sessions'
})
app.config.from_envvar('PRAVOSLAVLJE_SETTINGS', silent=True)


@app.teardown_appcontext
def close_db(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.template_global()
def url_for_static(filename, *args, **kwargs):
    return url_for('static', *args, filename=filename, **kwargs)


Profiler(app)
Session(app)

babel = Babel(app, 'sr_Cyrl_RS')

locale_prefixes = bidict({
    Locale('sr', territory='RS', script='Latn'): 'lat',
})


@app.url_defaults
def add_language_code(endpoint, values):
    if app.url_map.is_endpoint_expecting(endpoint, 'locale_prefix') and \
            g.locale in locale_prefixes:
        values['locale_prefix'] = locale_prefixes[g.locale]


@app.url_value_preprocessor
def set_locale_from_prefix(endpoint, values):
    if values:
        locale_prefix = values.pop('locale_prefix', None)
        if locale_prefix:
            if locale_prefix in locale_prefixes.inv:
                g.locale = locale_prefixes.inv[locale_prefix]
            return

    g.locale = babel.default_locale


@babel.localeselector
def babel_locale_selector():
    return g.locale


def localized_route(route, *args, **kwargs):
    def decorator(func):
        @app.route(route, *args, **kwargs)
        @app.route('/<locale_prefix>' + route, *args, **kwargs)
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'locale' not in g:
                return abort(404)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


@app.before_request
def set_endpoint():
    g.endpoint = request.endpoint


main_menu_items = {}


def main_menu_item(label):
    def decorator(func):
        main_menu_items[func.__name__] = label

        @wraps(func)
        def wrapper(*args, **kwargs):
            g.is_on_main_menu_item = True
            return func(*args, **kwargs)
        return wrapper
    return decorator


@localized_route('/')
@main_menu_item(_('Почетна'))
def index():
    return render_template('index.html')


@localized_route('/arhiva')
@main_menu_item(_('Архива'))
def archive():
    issues = query_db('SELECT * FROM issues ORDER BY date DESC')
    g.issue_per_year = []
    for year, year_issues in groupby(issues, lambda i: i['date'].year):
        g.issue_per_year.append((year, next(year_issues)))

    return render_template('archive.html')


@localized_route('/pretraga')
@main_menu_item(_('Претрага'))
def search():
    return render_template('search.html')


@localized_route('/pretplata')
@main_menu_item(_('Претплата'))
def subscription():
    return render_template('subscription.html')


@localized_route('/godina/<year>')
def year(year):
    from_ = '{}-01-01'.format(year)
    to = '{}-31-12'.format(year)
    g.issues = query_db('SELECT * FROM issues WHERE date BETWEEN ? AND ? ORDER BY date DESC', (from_, to))
    if g.issues:
        return render_template('year.html')
    else:
        return abort(404)


app.add_template_global(main_menu_items, 'main_menu_items')
