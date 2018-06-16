import os
import sqlite3

from flask import g

from app import app


def get():
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect(
            os.path.join(app.root_path, 'db.sqlite3'),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def query(query, args=(), one=False):
    cur = get().execute(query, args)
    results = getattr(cur, {True: 'fetchone', False: 'fetchall'}[one])()

    cur.close()
    if results is not None:
        return results[0] if one else results


@app.teardown_appcontext
def close(exception):
    if hasattr(g, 'db'):
        g.db.close()
