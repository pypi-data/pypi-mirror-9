# utils.py

r'''Misc database helper functions:

 * :class:`transaction`
 * :func:`now_truncated`
 * :func:`get_current_user_id`
'''

import sys
from datetime import datetime

from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import current_user


__all__ = ('transaction', 'now_truncated', 'get_current_user_id',)


# This needs db.init_app(app) to initialize the app context before any
# database accesses can be done.
db = SQLAlchemy()


def lookup_model(tablename):
    return current_app.dry_models_by_tablename[tablename]


def names_from_module(module):
    r'''Generates all names in module that don't start with an '_'.
    '''
    for name in dir(module):
        if not name.startswith('_'):
            yield getattr(module, name)


class transaction:
    r'''Ensures that the transaction is terminated at the end of code block.

    Does a `commit` on normal exit of the code block, and `rollback` if an
    exception is thrown out of the code block.

    This is simply a `context manager`_ to be used in the with statement.

    .. _context manager: https://docs.python.org/3/library/stdtypes.html#context-manager-types
    '''
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            commit_exc = False
            if exc_type is None:
                # FIX: Add check for validation errors
                #print("transaction commit")
                try:
                    db.session.commit()
                    return
                except Exception as e:
                    exc_type, exc_val, exc_tb = sys.exc_info()
                    assert exc_val is e
                    commit_exc = True
            #print("transaction rollback")
            db.session.rollback()
            if commit_exc:
                raise exc_val
        finally:
            #print("transaction close")
            db.session.close()


def now_truncated():
    r'''Return utcnow_, truncating the microseconds.

    Postgresql rounds microseconds while python truncates.  So they may
    not match, which screws up Last-Modified checks.

    .. _utcnow: https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow
    '''
    return datetime.utcnow().replace(microsecond=0)


def get_current_user_id():
    r'''Returns the current_user_ id, if a user is logged in.

    Else returns None.

    .. _current_user: https://flask-login.readthedocs.org/en/latest/#flask.ext.login.current_user
    '''
    if current_user.is_authenticated():
        return current_user.id
    return None

