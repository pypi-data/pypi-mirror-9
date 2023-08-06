# columns.py

r'''The :class:`DRY_Column` class to define the columns in your models.

Also includes the following column definition functions:

 * :func:`Phone`
 * :func:`Email`
 * :func:`PlainString`
 * :func:`PlainText`
 * :func:`Id`
 * :func:`Etag`
 * :func:`Auto_timestamp`
 * :func:`Auto_member_id`
'''

from sqlalchemy import text

from .utils import db
from .validation import (
    validate_min, validate_max, validate_min_length, validate_max_length,
    validate_phone_strict, validate_phone, no_html_chars, strip_value,
    validate_email,
)


__all__ = ('DRY_Column', 'Phone', 'Email', 'PlainString', 'PlainText', 'Id',
           'Etag', 'Auto_timestamp', 'Auto_member_id',
          )


class DRY_Column(db.Column):
    r'''Extends SQLAlchemy Column_.

    Adds the following optional keyword arguments:

     * dry_validators: adds a single validator, or a tuple/list of validators.
     * dry_min: adds a :func:`.validate_min` validator.
     * dry_max: adds a :func:`.validate_max` validator.
     * dry_min_length: adds a :func:`.validate_min_length` validator.
     * dry_max_length: adds a :func:`.validate_max_length` validator.

    .. _Column: http://docs.sqlalchemy.org/en/latest/core/metadata.html#sqlalchemy.schema.Column
    '''
    def __init__(self, *args, dry_min=None, dry_max=None,
                 dry_min_length=None, dry_max_length=None, dry_validators=(),
                 **kwargs):
        db.Column.__init__(self, *args, **kwargs)
        if dry_validators:
            if isinstance(dry_validators, (list, tuple)):
                dry_validators = tuple(dry_validators)
            else:
                dry_validators = (dry_validators,)
        if dry_min is not None:
            dry_validators += (validate_min(dry_min),)
        if dry_max is not None:
            dry_validators += (validate_max(dry_max),)
        if dry_min_length:
            dry_validators += (validate_min_length(dry_min_length),)
        if dry_max_length:
            dry_validators += (validate_max_length(dry_max_length),)
        self.dry_validators = dry_validators


def Phone(*args, strict=False, **kwargs):
    r'''A phone number column.

    This is a String with either a :func:`.validate_phone_strict` or
    :func:`.validate_phone`, depending on the `strict` parameter (default
    False).

    For non-strict phone numbers, defaults dry_max_length to 45.
    '''
    if strict:
        add_validators(kwargs, validate_phone_strict)
    else:
        kwargs.setdefault('dry_max_length', 45)
        add_validators(kwargs, validate_phone)
    return DRY_Column(db.String, *args, **kwargs)

def Email(*args, **kwargs):
    r'''An email address column.

    Includes the :func:`.validate_email` validator.

    Defaults dry_max_length to 300.
    '''
    kwargs.setdefault('dry_max_length', 300)
    add_validators(kwargs, strip_value, validate_email)
    return DRY_Column(db.String, *args, **kwargs)

def PlainString(*args, **kwargs):
    r'''A String, not allowing html tags.

    Includes the :func:`.no_html_chars` validator and :func:`.strip_value`.

    Defaults dry_min_length to 1 and dry_max_length to 300.
    '''
    kwargs.setdefault('dry_min_length', 1)
    kwargs.setdefault('dry_max_length', 300)
    add_validators(kwargs, strip_value, no_html_chars)
    return DRY_Column(db.String, *args, **kwargs)

def PlainText(*args, **kwargs):
    r'''A Text column, not allowing html tags.

    Includes the :func:`.no_html_chars` validator and :func:`.strip_value`.

    Defaults dry_min_length to 1 and dry_max_length to 10240.
    '''
    kwargs.setdefault('dry_min_length', 1)
    kwargs.setdefault('dry_max_length', 10240)

    # FIX: Why was this originally rstrip_value?
    #add_validators(kwargs, rstrip_value, no_html_chars)
    add_validators(kwargs, strip_value, no_html_chars)

    return DRY_Column(db.Text, *args, **kwargs)

def Id(*args, **kwargs):
    r'''An Integer for the id column.

    Defaults primary_key to True and nullable to False.
    '''
    kwargs.setdefault('primary_key', True)
    kwargs.setdefault('nullable', False)
    return DRY_Column(db.Integer, *args, **kwargs)

def Etag(*args, **kwargs):
    r'''An Integer for an etag column.

    Defaults nullable to False and server_default to text("1").
    '''
    kwargs.setdefault('nullable', False)
    kwargs.setdefault('server_default', text("1"))
    return DRY_Column(db.Integer, *args, **kwargs)

def Auto_timestamp(*args, **kwargs):
    r'''A DateTime column that defaults to localtimestamp.

    Defaults nullable to False and server_default to text("localtimestamp").
    '''
    kwargs.setdefault('nullable', False)
    kwargs.setdefault('server_default', text("localtimestamp"))
    return DRY_Column(db.DateTime, *args, **kwargs)

def Auto_member_id(*args, **kwargs):
    r'''An Integer ForeignKey to `members.id`.

    Sets the `ondelete` option to 'SET NULL'.
    '''
    return DRY_Column(db.Integer,
                      db.ForeignKey('members.id', ondelete='SET NULL'),
                      *args,
                      **kwargs)

def add_validators(kwargs, *validators):
    if 'dry_validators' not in kwargs:
        kwargs['dry_validators'] = []
    elif not isinstance(kwargs['dry_validators'], (tuple, list)):
        kwargs['dry_validators'] = [kwargs['dry_validators']]
    kwargs['dry_validators'].extend(validators)

