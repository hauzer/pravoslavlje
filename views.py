from functools import wraps
from itertools import groupby

import wtforms

from flask import abort, g, render_template
from flask_babelex import lazy_gettext as _
from flask_wtf import FlaskForm

from app import app
import db
import localization


app.add_template_global({}, 'main_menu_items')


def main_menu_item(label):
    def decorator(func):
        app.jinja_env.globals['main_menu_items'][func.__name__] = label

        @wraps(func)
        def wrapper(*args, **kwargs):
            g.is_on_main_menu_item = True
            return func(*args, **kwargs)
        return wrapper
    return decorator


@localization.route('/')
@main_menu_item(_('Почетна'))
def index():
    return render_template('index.html')


@localization.route('/arhiva')
@main_menu_item(_('Архива'))
def archive():
    issues = db.query('SELECT * FROM issues ORDER BY date DESC')
    g.issue_per_year = []
    for year, year_issues in groupby(issues, lambda i: i['date'].year):
        g.issue_per_year.append((year, next(year_issues)))

    return render_template('archive.html')


class SubscribeForm(FlaskForm):
    name = wtforms.StringField(
        _('Ваше име'),
        validators=[
            wtforms.validators.DataRequired('asdsada'),
            wtforms.validators.InputRequired(),
            wtforms.validators.Length(min=5, max=40),
        ]
    )
    email = wtforms.StringField(
        _('Ваша е-пошта'),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.InputRequired(),
            wtforms.validators.Length(min=5, max=40),
            wtforms.validators.Email(),
        ]
    )
    message = wtforms.TextAreaField(
        _('Ваша порука'),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.InputRequired(),
            wtforms.validators.Length(max=1000),
        ]
    )


@localization.route('/pretplata', methods=('GET', 'POST'))
@main_menu_item(_('Претплата'))
def subscription():
    form = SubscribeForm()
    if form.validate_on_submit():
        return abort(404)
    return render_template('subscription.html', form=form)
    # pass


@localization.route('/godina/<year>')
def year(year):
    from_ = '{}-01-01'.format(year)
    to = '{}-31-12'.format(year)
    g.issues = db.query('SELECT * FROM issues WHERE date BETWEEN ? AND ? ORDER BY date DESC', (from_, to))
    if g.issues:
        return render_template('year.html')
    else:
        return abort(404)
