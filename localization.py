from functools import wraps

from bidict import bidict
from flask import abort, g
from flask_babelex import Babel, Locale

from app import app


babel = Babel(app, 'sr_Cyrl_RS')

locale_prefixes = bidict({
    Locale('sr', territory='RS', script='Latn'): 'lat',
})


@app.url_defaults
def add_language_code(endpoint, values):
    if app.url_map.is_endpoint_expecting(
            endpoint, 'locale_prefix'
            ) and g.locale in locale_prefixes:
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


def route(route, *args, **kwargs):
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
