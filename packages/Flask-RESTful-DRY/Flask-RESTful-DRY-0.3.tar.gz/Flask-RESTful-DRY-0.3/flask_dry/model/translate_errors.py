# translate_errors.py

r'''Translates Postgresql database errors back to "user speak".
'''

import re

from flask import current_app

from .utils import lookup_model


_get_name_re = re.compile(r'"([^"]*)"[^"]*$')

def translate_error(exc_val):
    r'''Returns a sequence of (column, message).
    '''
    print("translate_error: args", exc_val.args)
    print("translate_error: connection_invalidated",
          exc_val.connection_invalidated)
    print("translate_error: detail", exc_val.detail)
    print("translate_error: statement", exc_val.statement)
    print("translate_error: params", exc_val.params)
    pgexc = exc_val.orig
    pgcode = pgexc.pgcode
    pgerror = pgexc.pgerror
    lines = pgerror.split('\n')
    m = _get_name_re.search(lines[0])
    if m:
        name = m.group(1)
    else:
        name = None

    if pgcode == '23502':  # not_null_violation
        assert name
        #print("non_null_violation", name)
        _get_table_key(exc_val)
        return (name, 'Required field.'),
    if pgcode == '23505':  # unique_violation
        _get_table_key(exc_val)
        if name in current_app.dry_unique_constraints:
            #print("unique_constraints", name,
            #      current_app.dry_unique_constraints[name])
            return current_app.dry_unique_constraints[name]
    if pgcode == '23503':  # foreign_key_violation
        _get_table_key(exc_val)
        if name in current_app.dry_foreign_key_constraints:
            #print("foreign_key_constraints", name,
            #      (current_app.dry_foreign_key_constraints[name],))
            return current_app.dry_foreign_key_constraints[name],

    #
    # See: http://www.postgresql.org/docs/current/static/errcodes-appendix.html#ERRCODES-TABLE
    # 01004: string_data_right_truncation
    # 22000: data_exception
    # 22021: character_not_in_repertoire
    # 22007: invalid_datetime_format
    # 22004: null_value_not_allowed
    # 22003: numeric_value_out_of_range
    # 22026: string_data_length_mismatch
    # 22001: string_data_right_truncation
    # 23000: integrity_constraint_violation
    # 23502: not_null_violation
    # 23503: foreign_key_violation
    # 23505: unique_violation
    # 23514: check_violation
    # 40002: transaction_integrity_constraint_violation
    # 40001: serialization_failure
    # 40P01: deadlock_detected
    # 42804: datatype_mismatch
    #

    cause = pgexc.__cause__
    #print("name", name)
    #print("pgcode", repr(pgcode))
    #print("cause", cause)
    #print("dir", dir(pgexc))

    d = dict(pgcode=pgcode, pgerror=pgerror, name=name,
             cause=str(cause),
             pgexc={k: repr(getattr(pgexc, k))
                    for k in dir(pgexc)
                    if not k.startswith('_')},
            )
    if cause:
        d['cause_exc'] = {k: repr(getattr(cause, k))
                          for k in dir(cause)
                          if not k.startswith('_')}
    #print("unknown", name)
    return ('unknown', d),


_table_name_re = re.compile(
  r'(?: *update +(\w+) | *insert +into +(\w+) | *delete +from +(\w+) )',
  re.I
)

def _get_table_key(exc_val):
    r'''Returns command, tablename, key.

    Command is one of: 'insert', 'update' or 'delete'.

    If key can not be determined (such as for an autoincrement insert row),
    None if returned.

    If nothing can be determined, returns None, None, None.
    '''
    match = _table_name_re.match(exc_val.statement)
    if not match:
        return None, None, None
    if match.group(1):
        command = 'update'
        table = match.group(1)
    elif match.group(2):
        command = 'insert'
        table = match.group(2)
    else:
        assert match.group(3)
        command = 'delete'
        table = match.group(3)
    model = lookup_model(table)
    key_column = model._dry_key_column()
    params = exc_val.params
    if key_column in params:
        print("found", key_column)
        key = params[key_column]
    else:
        tbl_key = "{}_{}".format(table, key_column)
        if tbl_key in params:
            print("found", tbl_key)
            key = params[tbl_key]
        else:
            print("key not found")
            key = None
    print("command", command, "table", table,
          "key_column", key_column, "key", key)
    return command, table, key

