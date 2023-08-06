# steps.py

r'''These are the steps to choose from to implement an HTTP method.

The milestones are:

    - 110 check_csrf

    - 120 header checks:

        - check_content
        - check_accepts

    - 200 authorize

      All processing leading up to, and including, the authorization check.
      This examines the context.authorization_requirements and will set
      context.role to the selected Requirement.  It also copies any _overrides
      from that Requirement into the context.  For example, different
      Requirements may set various context *columns differently.

      If the authorization check fails, abort(401) (UNAUTHORIZED) is called
      immediately, possibly including a reason.

    - 270 validate_columns

    - 280 report_errors

    - 290 abort_no_updates

    - 300 check_conditionals
'''

from collections import defaultdict
from datetime import date, time, datetime
import hashlib
import json

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from werkzeug.http import parse_accept_header
from flask import request, make_response, current_app
from flask.ext.restful import abort
from flask.ext.restful.representations.json import settings as json_settings
from flask.ext.login import current_user, login_fresh
from flask.ext.wtf.csrf import validate_csrf

from .step_utils import step, if_needed, parameterize
from .utils import cache, datetime_to_header_format, get_universal
from . import links
from .updated_items import make_updated_item, make_sublist
from .column_auth import item_column_auth
from ..model.utils import db
from ..model.model import Model


# Sent by client using 'csrf_token' in /login response.
Csrf_header = 'X-CSRF-Token'


class QuitSteps(BaseException):
    pass


# Authorization:
@step('authorize',
      'authorization_requirements,authorization_context,cache_public',
      'role,cache_public',
      milestone=200)
def authorize(context):
    r'''Does the authorization check against `authorization_context`.

    Selects the authorization Requirement from `authorization_requirements`
    that validates for the current_user against the `authorization_context`.

    Aborts with 401 UNAUTHORIZED if no Requirements match.

    Sets role to the selected Requirement, or None if there are no
    authorization_requirements.

    Sets cache_public to False if there are any authorization_requirements.
    '''
    requirements = context.authorization_requirements
    context.role = None
    if requirements:
        if current_user.is_authenticated() and current_user.superuser and \
           login_fresh():
            if context.debug:
                print("current_user", current_user.id, "is superuser!")
            context.role = requirements[0]
        else:
            if context.debug:
                if current_user.is_authenticated():
                    print("current_user", current_user.id)
                else:
                    print("current_user", None)
            auth_context = context.authorization_context
            reason = None
            for r in requirements:
                valid = auth_context.meets(r, context.debug)
                if valid == True:
                    context.role = r
                    break
                if valid != False and reason is None:
                    # Take the first reason (from the highest requirement that
                    # this user meets).
                    reason = valid
            else:
                if reason is None:
                    # 401 UNAUTHORIZED
                    abort(401)
                else:
                    # 401 UNAUTHORIZED
                    abort(401, reason=reason)
        if context.role is not None:
            context.role._overrides.copy_into(context)
        context.cache_public = False

@step('authorize', '', '', milestone=200)
def is_authenticated(context):
    if not current_user.is_authenticated():
        # 401 UNAUTHORIZED
        abort(401, message="Member not signed in.")

@step('authorize', '', '', milestone=200)
def is_not_authenticated(context):
    if current_user.is_authenticated():
        # 401 UNAUTHORIZED
        abort(401, message="Already logged in, logout first.")


# Validation
#
# Data validation for POST(create) and PUT(update) is done in 5 steps:
#
# 1. Only allow permitted columns.  This creates a dict of updated_columns.
#    Columns that don't change in a PUT(update) are not included (and also not
#    reported if not permitted).
#
#    POST: get_insert_item_columns   new_item => updated_columns
#    PUT:  get_updated_item_columns  new_item,item => updated_columns,
#
# 2. Do the column-level validation.  These are the validations passed back to
#    the client through the metadata apis.
#
#    POST: validate_new_columns      updated_columns => updated_columns,
#                                                       errors, revised
#    PUT:  validate_updated_columns  updated_columns => updated_columns,
#                                                       errors, revised
#
# 3. Do cross column validation.  This is done by the model before the row
#    (item) from the database is updated.  The model has access to both the
#    old and new values and can see what changed.  These functions add system
#    updated attributes to be inserted/updated into the row (like modification
#    timestamps).
#
#    POST: validate_insert           updated_columns => updated_columns,
#                                                       errors, revised
#          calls :method:`.Model.validate_insert` on the model
#
#    PUT:  validate_update           updated_columns,item => updated_columns,
#                                                            errors, revised,
#          calls :method:`.Model.validate_update` on the model
#
# 4. Does any final validation and updates the database.  This validation is
#    done after the row has been completely updated, just before it is written
#    back to the database.  Again, this is done by the model by calling
#    :method:`.Model.dry_cross_validate`.  This is an old validate method that
#    currently doesn't do anything and may be deleted in the future.
#
#    POST: create_item               updated_columns => item, errors, revised,
#                                                       final_last_modified,
#                                                       final_etag
#    PUT:  update_item               updated_columns => errors, revised,
#                                                       final_last_modified,
#                                                       final_etag
#
# 5. Report any errors reported from the database (e.g., unique constraint
#    violation).  This is done by :method:`.Model.check_database_errors`, which
#    is called by both step functions above (in step 4).
#


@step('check_csrf', milestone=110)
def check_csrf(context):
    if current_user.is_authenticated():
        if Csrf_header not in request.headers:
            # 403 FORBIDDEN
            abort(403, message="Missing CSRF Token")
        csrf = request.headers[Csrf_header]
        if not (current_app.testing and csrf == 'Get Out of Jail Free') and \
           not validate_csrf(csrf):
            # 403 FORBIDDEN
            abort(403, message="Invalid CSRF Token")

@step('check_content', milestone=120)
def no_content(context):
    if request.content_length:
        # 400 BAD REQUEST
        abort(400, message="No content expected")

@step('check_content', milestone=120)
def json_content_type(context):
    if request.mimetype != 'application/json':
        # 415 UNSUPPORTED MEDIA TYPE
        abort(415, message="Only application/json accepted")

@step('check_accepts', milestone=120)
def accepts_json(context):
    if 'Accept' not in request.headers:
        # Client's not fussy, so we're OK!
        return
    accept = parse_accept_header(request.headers['Accept'])
    if 'application/json' in accept:
        if accept.quality('application/json') == 0.0:
            # 406 NOT ACCEPTABLE
            abort(406, message="Only application/json supported")
    elif 'application/*' in accept:
        if accept.quality('application/*') == 0.0:
            # 406 NOT ACCEPTABLE
            abort(406, message="Only application/json supported")
    elif '*/*' in accept:
        if accept.quality('*/*') == 0.0:
            # 406 NOT ACCEPTABLE
            abort(406, message="Only application/json supported")
    else:
        # 406 NOT ACCEPTABLE
        abort(406, message="Only application/json supported")


# Check conditionals
#
# from: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
#
# If-Match:            - Should return 412 PRECONDITION FAILED only if the
#                        entity etag does not match (or there is no entity).
#                      - This can not override anything but a 2xx status (or
#                        other 412 status).
#                      - Must use strong comparision.
#                      - Expected with PUT and DELETE.
#
# If-None-Match:       - Must not perform the operation if etag matches, unless
#                        required to do so by If-Modified-Since header.
#                      - If used with GET, return 304 NOT MODIFIED (must not
#                        return 304 If-Modified-Since would not return 304).
#                      - Otherwise (e.g., PUT) return 412.
#                      - Weak comparisions only allowed for GET.
#                      - This can not override anything but a 2xx or 304 status.
#                      - Undefined how this interacts with If-Match or
#                        If-Unmodified-Since.
#                      - Used on GET to check for new versions, and PUT (with
#                        etag "*") to make sure that the entity does not
#                        already exist.
#
# If-Modified-Since:   - Should return 304 NOT MODIFIED if not modified (and
#                        only if If-None-Match would return 304 as well).
#                      - Ignored if invalid date (incorrect format or date in
#                        future) is passed.
#                      - Undefined how this interacts with an
#                        If-Unmodified-Since or If-Match header.
#                      - Only acted on for GET.
#
#                      304: must not include a message body, and MUST include:
#                             ETag/Content-Location if they would have been
#                               sent in a 200 response
#                             Expires/Cache-Control/Vary if the header value
#                               might differ from previous responses.
#
# If-Unmodified-Since: - Return 412 if modified
#                      - This can not override anything but a 2xx or 412 status.
#                      - If the date is invalid, ignore this header.
#                      - Undefined how this interacts with an
#                        If-Modified-Since or If-None-Match header.



@if_needed('get_versions', 'item.1', 'last_modified,etag')
def get_item_versions(context):
    context.last_modified = get_universal(context.item,
                                          'last_modified_timestamp')
    context.etag = get_universal(context.item, 'etag')

@step('check_conditionals', milestone=300)
def no_conditionals(context):
    for header in ('If-Modified-Since', 'If-Unmodified-Since',
                   'If-Match', 'If-None-Match'):
        if header in request.headers:
            abort(400,
                  message='{}: Conditional header not allowed'.format(header))

@step('check_conditionals', 'last_modified,etag,headers', milestone=300)
def check_get_conditionals(context):
    r'''Checks conditional headers for GET.

    This aborts the transaction (rollback) if a status 304 NOT MODIFIED is
    generated.
    '''
    # Check If-Unmodifed-Since and If-Match headers (normally not used on GET):
    if_unmodified_since = request.if_unmodified_since
    if if_unmodified_since and \
       if_unmodified_since <= datetime.utcnow() and \
       context.last_modified is not None and \
       context.last_modified > if_unmodified_since:
        # 412: PRECONDITION FAILED
        abort(412)

    if 'If-Match' in request.headers and \
       not request.if_match.contains(str(context.etag)):
        # 412: PRECONDITION FAILED
        abort(412)

    # Only return a 304 if there is either an If-Modified-Since or
    # If-None-Match that shows no change and neither If-Modified-Since nor
    # If-None-Match shows a change.

    no_change = False
    changed = False

    if_modified_since = request.if_modified_since
    if if_modified_since and if_modified_since <= datetime.utcnow() and \
       context.last_modified is not None:
        if context.last_modified <= if_modified_since:
            no_change = True
        else:
            changed = True

    if 'If-None-Match' in request.headers:
        if request.if_none_match.contains(str(context.etag)):
            no_change = True
        else:
            changed = True

    if no_change and not changed:
        # 304: NOT MODIFIED
        context.response = make_response('', 304, context.headers)
        raise QuitSteps

@step('check_conditionals', 'method,last_modified,etag', milestone=300)
def check_update_conditionals(context):
    r'''Checks conditional headers for PUT/DELETE.

    If last_modified is None (the default in dry_resource.py),
    If-Unmodified-Since is not allowed.  Otherwise, it's required.
    '''
    # Verify absense of If-Modified-Since and If-None-Match headers.
    for header in ('If-Modified-Since', 'If-None-Match'):
        if header in request.headers:
            abort(400,
                  message='{}: Conditional header not allowed'.format(header))

    # Verify presence or absense of If-Unmodified-Since header.
    last_modified = context.last_modified
    if last_modified is None:
        if 'If-Unmodified-Since' in request.headers:
            abort(400, message="If-Unmodified-Since header not supported on {}"
                                 .format(context.method.upper()))
    else:
        if 'If-Unmodified-Since' not in request.headers:
            abort(400, message="If-Unmodified-Since header required on {}"
                                 .format(context.method.upper()))

    # Verify presence of If-Match header.
    if 'If-Match' not in request.headers:
        abort(400, message="If-Match header required on {}"
                             .format(context.method.upper()))

    # Check precondition(s).
    if last_modified is not None and \
       last_modified > request.if_unmodified_since or \
       not request.if_match.contains(str(context.etag)):
        print("last_modified", last_modified, "etag", context.etag)
        # 412: PRECONDITION FAILED
        abort(412)


# Core processing

@parameterize
@if_needed('unpack_json_parameters', 'errors',
           'required_parameters,optional_parameters,errors')
def unpack_json_parameters(*required_parameters, context,
                           **optional_parameters):
    parameters = request.json.copy()
    for p in required_parameters:
        if p not in parameters:
            context.errors[p].append("{} not provided".format(p.capitalize()))
        else:
            setattr(context, p, parameters.pop(p))
    for p, default in optional_parameters.items():
        if p not in parameters:
            setattr(context, p, default)
        else:
            setattr(context, p, parameters.pop(p))
    for p in parameters.keys():
        context.errors[p].append("{} unexpected".format(p.capitalize()))

@if_needed('get_key_columns', 'columns_to_keys', 'key_columns')
def get_key_columns(context):
    r'''Creates a mapping from column_name to column_value.

    Remaps the key names in columns_to_keys to column names and looks up each
    key in context for the value.
    '''
    context.key_columns = {c: getattr(context, k)
                           for c, k in context.columns_to_keys.items()}

@if_needed('get_item', 'keys,auth_model', 'auth_item')
def get_auth_item(context):
    assert len(context.keys) == 1
    id = getattr(context, context.keys[0])
    query = context.auth_model.query.filter_by(id=id)
    try:
        context.auth_item = query.one()
    except MultipleResultsFound:
        abort(500,
              debug="Multiple responses found for {}: id={}"
                      .format(context.auth_model.__name__, id))
    except NoResultFound:
        abort(context.auth_model.get_status(id))

@if_needed('get_item', 'model,key_columns', 'auth_item,item')
def get_item(context):
    r'''Retrieves one row.

    Places the row in both auth_item for authorization and item to return from
    a GET call for an item.  Sometimes this is only needed for one or the
    other purposes.

    There are situations (e.g., metadata) where this step is needed for
    authorization, and some other step is needed to create the item to return.
    In this case, this step will be placed early in the steps list to satisfy
    the `authorize` step's need.  The other step will be placed later to
    satisfy the results needs and will override the `item` value.

    There are no situations where this step is needed for the `item`, and some
    other step is needed for the `auth_item`.  So the `auth_item` never needs
    to be overwritten (though it is sometimes ignored).
    '''
    query = context.model.query.filter_by(**context.key_columns)
    try:
        context.auth_item = context.item = query.one()
    except MultipleResultsFound:
        abort(500,
              debug="Multiple responses found for {}"
                      .format(
                        ', '.join("{}={}".format(k, v)
                                  for k, v
                                   in sorted(context.key_columns.items()))))
    except NoResultFound:
        if len(context.key_columns) == 1:
            # model.get_status figures out whether it's 404 NOT FOUND or
            # 410 GONE.
            abort(context.model.get_status(
                                  tuple(context.key_columns.values())[0]))
        else:
            abort(404)

@if_needed('get_current_user', '', 'member,member_id,known_keys')
def get_current_user(context):
    if current_user.is_authenticated():
        context.member = current_user
        id = context.member_id = context.member.id
        context.known_keys = dict(member_id=id)
    else:
        context.member = None
        context.member_id = None
        context.known_keys = {}

@if_needed('get_query', 'model', 'query')
def get_query(context):
    context.query = context.model.get_query()

@step('query_list', 'keys,model,query', 'query')
def query_list(context):
    model = context.model
    context.query = context.query.filter(
                      *[getattr(model, key) == getattr(context, key)
                        for key in context.keys])

@if_needed('get_list', 'query', 'output_list')
def get_list(context):
    context.output_list = context.query.all()

@if_needed('init_errors', '', 'errors,revised')
def init_errors(context):
    r'''Initializes the `errors` and `revised` attributes on context.
    '''
    context.errors = defaultdict(list)
    context.revised = {}

@if_needed('init_errors', 'new_list', 'errors')
def init_list_errors(context):
    r'''Initializes the `errors` attribute on context.
    '''
    num_items = len(context.new_list)
    context.errors = [defaultdict(list) for _ in range(num_items)]
    #context.revised = [{} for _ in range(num_items)]

@if_needed('get_new_item', 'model', 'new_item')
def get_new_item(context):
    r'''Places the json input payload into `new_item`.

    Converts datetime columns into datetime objects.
    '''
    context.new_item = _convert_datetimes(context.model._dry_column_info,
                                          request.json)

def _convert_datetimes(column_info, d):
    ans = d.copy()
    for column in d.keys():
        t = column_info.get(column)
        if t is not None:
            col_type = t.col_type
            if col_type == 'datetime':
                ans[column] = as_datetime(ans[column])
            elif col_type == 'date':
                ans[column] = as_date(ans[column])
            elif col_type == 'time':
                ans[column] = as_time(ans[column])
    return ans

@if_needed('get_new_item', 'model', 'item.2')
def load_column_info(context):
    r'''Loads column_info into item.

    Includes sublists.
    '''
    context.item = _make_new_item_column_info(context.model)

@if_needed('get_new_item', '', 'new_list')
def get_new_list(context):
    r'''Places the json input payload into `new_list`.

    Converts datetime columns into datetime objects.
    '''
    column_info = context.model._dry_column_info
    context.new_list = [_convert_datetimes(column_info, x)
                        for x in request.json]

def _make_new_item_column_info(model):
    ans = model._dry_column_info.copy()
    for column, (child_model, _) in model._dry_relationships.items():
        ans[column] = _make_new_item_column_info(child_model)
    return ans

@if_needed('get_item', 'new_item', 'item')
def use_new_item_as_item(context):
    r'''Copies new_item to item.

    This step is not currently used.
    '''
    context.item = context.new_item


@if_needed('get_updated_columns', 'new_item,item.1,model,errors',
           'updated_columns,errors,changed')
def get_updated_item_columns(context):
    r'''Populates updated_columns with columns that have changed from new_item.

    Updated_columns is an :class:`.updated_item`.

    Unauthorized columns are reported, as well as illegal parent keys or
    unknown child ids.
    '''
    context.updated_columns = \
      make_updated_item(context.model, context.new_item, context.item,
                        context.errors, context.column_auth_for_update())
    context.changed = context.updated_columns._status != 'unchanged'

@if_needed('get_updated_columns', 'new_item,model,errors',
           'updated_columns,errors')
def get_insert_item_columns(context):
    r'''Populates updated_columns with legal columns from new_item.

    Updated_columns is a :class:`.new_item`.

    Unauthorized columns are reported, as well as illegal parent keys or child
    ids provided in the new_item.
    '''
    context.updated_columns = \
      make_updated_item(context.model, context.new_item, None,
                        context.errors, context.column_auth_for_insert())

@step('get_updated_columns',
      'new_list,output_list.1,model,errors,keys',
      'updated_list,errors,changed')
def get_updated_list_columns(context):
    r'''Figures out what changed between `output_list` and `new_list`.

    Sets updated_list to an :class:`.updated_list` object.

    Unauthorized columns are reported, as well as illegal parent keys or child
    ids provided in the new_item.
    '''
    assert len(context.keys) == 1
    key = context.keys[0]
    value = getattr(context, key)
    context.updated_list = make_sublist(context.model, context.new_list,
                                        context.output_list, context.errors,
                                        item_column_auth(context), key, value)
    context.changed = context.updated_list._status != 'unchanged'

@step('abort_no_updates', 'changed,errors,revised',
      milestone=290)
def abort_no_updates(context):
    if not context.changed:
        kwargs = dict(message="No change")
        errors = strip_errors(context.errors)
        if errors:
            kwargs['errors'] = errors
        revised = strip_revised(context.revised)
        if revised:
            kwargs['revised'] = revised
        # 409 CONFLICT
        abort(409, **kwargs)

@step('abort_no_updates', 'changed,errors,revised',
      milestone=290)
def abort_no_list_updates(context):
    if not context.changed:
        kwargs = dict(message="No change")
        errors = strip_errors_list(context.errors)
        if errors:
            kwargs['errors'] = errors
        revised = strip_revised_list(context.revised)
        if revised:
            kwargs['revised'] = revised
        # 409 CONFLICT
        abort(409, **kwargs)

@step('model_validation', 'updated_columns.2,role,now,errors,revised',
      'updated_columns.3,errors,revised')
def validate_update(context):
    r'''Does cross validation checks between the updated_columns and item.

    Also adds system_updated_attributes (e.g., time modified columns).

    Calls validate_update on the model to do this.
    '''
    _model_validation(context, context.updated_columns, context.role,
                      context.now, context.errors, context.revised,
                      context.updated_columns._old_item.validate_update)

@step('model_validation', 'updated_columns.2,role,now,errors,revised',
      'updated_columns.3,errors,revised')
def validate_insert(context):
    r'''Does cross validation checks in updated_columns.

    Also adds system_updated_attributes (e.g., time modified columns).

    Calls validate_insert on the model to do this.
    '''
    _model_validation(context, context.updated_columns, context.role,
                      context.now, context.errors, context.revised,
                      context.updated_columns._model.validate_insert)

def _model_validation(context, updated_columns, role, now, errors, revised,
                      validation_method):
    validation_method(context, updated_columns, role, now, errors, revised)

    for column, updated_list in updated_columns.sublists():
        revised_list = \
          _model_list_validation(context, updated_list, role, now,
                                 errors[column], revised.get(column))

        if any(revised_list):
            revised[column] = revised_list

@step('model_validation',
      'updated_list.2,role,now,errors,revised',
      'updated_list.3,errors,revised')
def validate_updates_in_list(context):
    revised_list = _model_list_validation(context, context.updated_list,
                                          context.role, context.now,
                                          context.errors, context.revised)
    if any(revised_list):
        context.revised = revised_list

def _model_list_validation(context, updated_list, role, now, errors_list,
                           revised_list=None):
    if revised_list is None:
        revised_list = [{} for _ in range(len(errors_list))]
    for updated_item in updated_list.updated_items:
        if updated_item._status in ('updated', 'new'):
            _model_validation(context, updated_item, role, now,
                              errors_list[updated_item._index],
                              revised_list[updated_item._index],
                              update_item._old_item.validate_update
                                if updated_item._status == 'updated'
                                else updated_item._model.validate_insert)
    return revised_list

@step('validate_columns', 'updated_columns,errors,revised',
      'updated_columns.2,errors,revised',
      milestone=270)
def validate_updated_columns(context):
    r'''Calls :method:`.base_data.column_info.Column_info.validate` on each
    column.
    '''
    _validate_columns(context.updated_columns, context.errors, context.revised)

@step('validate_columns', 'updated_columns,errors,revised',
      'updated_columns.2,errors,revised',
      milestone=270)
def validate_new_columns(context):
    r'''Calls :method:`.base_data.column_info.Column_info.validate` on each
    column.
    '''
    _validate_columns(context.updated_columns, context.errors, context.revised)

def _validate_columns(updated_columns, errors, revised):
    model = updated_columns._model
    for column, value in tuple(updated_columns.user_updated_attributes()):
        new_value, column_errors = \
          model.dry_get_column_info(column) \
               .validate(value, updated_columns._status == 'updated')
        if new_value != value:
            revised[column] = new_value
        if column_errors:
            errors[column].extend(column_errors)
            del updated_columns[column]
    for column, updated_list in tuple(updated_columns.sublists()):
        revised_list = _validate_columns_in_list(updated_list, errors[column])
        if revised_list:
            revised[column] = revised_list

@step('validate_columns', 'updated_list,errors',
      'updated_list.2,errors,revised')
def validate_updated_columns_in_list(context):
    r'''Calls :method:`.base_data.column_info.Column_info.validate` on each
    column.
    '''
    context.revised = _validate_columns_in_list(context.updated_list,
                                                context.errors)

def _validate_columns_in_list(updated_list, errors_list):
    r'''Validates the columns in the items within `updated_list`.

    Appends errors to corresponding elements in errors_list.

    Returns revised_list if any values were revised, else None.
    '''
    revised_list = [{} for _ in range(len(errors_list))]
    for updated_item in updated_list.updated_items:
        if updated_item._status in ('updated', 'new'):
            _validate_columns(updated_item,
                              errors_list[updated_item._index],
                              revised_list[updated_item._index])
    if any(revised_list):
        return revised_list
    return None

@step('update_item',
      'updated_columns,now,errors,revised',
      'item.2,errors,revised,final_last_modified,final_etag')
def update_item(context):
    r'''Updates `_old_item` in `updated_columns`.

    Calls :method:`.Model.dry_cross_validate` and
    :method:`.Model.check_database_errors`.
    '''
    context.final_last_modified, context.final_etag = \
      _update_item(context.updated_columns, context.now, context.errors,
                   context.revised)

def _update_item(updated_item, now, errors, revised):
    r'''Returns final_last_modified, final_etag.
    '''
    item = updated_item._old_item
    for column, value in updated_item.updated_attributes():
        setattr(item, column, value)
    for column, updated_list in updated_item.sublists():
        revised_list = _update_list(updated_list, now,
                                    errors[column], revised.get(column))
        if revised_list:
            revised[column] = revised_list
    item.dry_cross_validate(now, revised, errors)
    item.check_database_errors(errors)
    return (getattr(item, 'last_modified_timestamp', None),
            getattr(item, 'etag', None))

@step('update_columns',
      'updated_list,now,errors,revised',
      'output_list.2,errors,revised')
def update_list(context):
    context.revised = _update_list(context.updated_list, context.now,
                                   context.errors, context.revised)

def _update_list(updated_list, now, errors_list, revised_list=None):
    if not revised_list:
        revised_list = [{} for _ in range(len(errors_list))]
    for deleted_item in updated_list.get_by_status('deleted'):
        old_item = deleted_item._old_item
        print("_update_list deleting", old_item)
        old_item.dry_delete(now)
        delete_errors = defaultdict(list)
        old_item.check_database_errors(delete_errors)
        assert not delete_errors
    for updated_item in updated_list.get_by_status('updated'):
        i = updated_item._index
        _update_item(updated_item, now, errors_list[i], revised_list[i])
    for new_item in updated_list.get_by_status('new'):
        print("_update_list creating", new_item)
        i = new_item._index
        _create_item(new_item, now, errors_list[i], revised_list[i])
    if any(revised_list):
        return revised_list
    return None

@step('create_item', 'updated_columns,now,errors,revised',
      'errors,revised,item,final_last_modified,final_etag')
def create_item(context):
    r'''Creates `item` from `updated_columns`.

    Calls :method:`.Model.dry_cross_validate`, then adds the new `item` to the
    database session and calls :method:`.Model.check_database_errors`.
    '''
    context.item, context.final_last_modified, context.final_etag = \
      _create_item(context.updated_columns, context.now, context.errors,
                   context.revised)

def _create_item(new_item, now, errors, revised):
    r'''Returns (new item, last_modified_timestamp, etag).
    '''
    # Insert parent:
    normal_columns = {k: v for k, v in new_item.updated_attributes()}
    model = new_item._model
    item = model(**normal_columns)
    item.dry_cross_validate(now, revised, errors)
    db.session.add(item)
    item.check_database_errors(errors)

    # Insert children:
    parent_key = getattr(item, model._dry_key_column(), None)
    print("_create_item got parent_key", parent_key)
    for column, updated_list in new_item.sublists():
        assert not tuple(updated_list.get_by_status('updated'))
        assert not tuple(updated_list.get_by_status('deleted'))
        errors_list = errors[column]
        revised_list = revised.get(column)
        if not revised_list:
            revised_list = [{} for _ in range(len(errors_list))]
        for new_child in updated_list.get_by_status('new'):
            assert parent_key is not None
            new_child.add_system_updated_attribute(
              updated_list.parent_link_column, parent_key)
            i = new_child._index
            _create_item(new_child, now, errors_list[i], revised_list[i])
        if any(revised_list):
            revised[column] = revised_list

    return (item, getattr(item, 'last_modified_timestamp', None),
            getattr(item, 'etag', None))

@step('delete_item', 'item,now', 'output')
def delete_item(context):
    r'''Logically deletes an item.

    Whether the item is actually deleted, or just flagged as deleted is
    handled in the model through the dry_delete method.
    '''
    context.item.dry_delete(context.now)

@step('create_metadata', 'output,metadata_type', 'output')
def create_metadata(context):
    context.output = _create_metadata(context.output, context.metadata_type)

def _create_metadata(item, metadata_type):
    def convert(column_info):
        if isinstance(column_info, dict):
            return dict(type="children",
                        child=_create_metadata(column_info, metadata_type))
        ans = dict(type=column_info.col_type,
                   nullable=column_info.nullable,
                  )
        if metadata_type == 'create':
            ans['optional'] = column_info.optional
        ans.update(column_info.validator_info())
        return ans
    return {column: convert(column_info) if column != '_links'
                                         else column_info
            for column, column_info in item.items()}


# Preparing the response

@step('report_errors', 'errors,revised', milestone=280)
def report_errors(context):
    errors = strip_errors(context.errors)
    if errors:
        revised = strip_revised(context.revised)
        if revised:
            abort(400, revised=revised, errors=errors)
        else:
            abort(400, errors=errors)

@step('filter_output_columns', 'item,column_auth_method', 'output')
def filter_item_columns(context):
    r'''Filter allowed columns from `item`, creating `output`.
    '''
    action_column_auth = getattr(context, context.column_auth_method)()
    context.output = _filter_item(context.item, context, action_column_auth)

def _filter_item(item, context, action_column_auth):
    def convert(key, value):
        if isinstance(value, (list, tuple)) and value and \
           isinstance(value[0], (dict, Model)):
            sub_action_column_auth = \
              action_column_auth.get_sublist_column_auth(key)
            return [_filter_item(x, context, sub_action_column_auth)
                    for x in value]
        elif isinstance(value, dict):
            # This should only happen for a sublist in metadata.  Then the
            # value is the column info for the sublist.
            sub_action_column_auth = \
              action_column_auth.get_sublist_column_auth(key)
            return _filter_item(value, context, sub_action_column_auth)
        else:
            return value
    return {key: convert(key, get_universal(item, key))
            for key in action_column_auth.allowed(item.keys())}

@step('filter_output_columns', 'output_list,column_auth_method',
      'output_list.2')
def filter_list_columns(context):
    action_column_auth = getattr(context, context.column_auth_method)()
    context.output_list = [_filter_item(x, context, action_column_auth)
                           for x in context.output_list]

@step('convert_links', 'output,model', 'output.3')
def convert_item_links(context):
    convert_links_for_item(context.output, context.model)

@step('convert_links', 'output_list.2,model', 'output_list.3')
def convert_list_links(context):
    for x in context.output_list:
        convert_links_for_item(x, context.model, add_top_self_link=True)

def convert_links_for_item(item, model, add_top_self_link=False):
    def link_for_key(column, model):
        key = item.get(column)
        if key is not None and hasattr(model, 'item_resource'):
            return model.item_resource.link_for_key(key)
        return None
    if add_top_self_link and len(model._dry_primary_keys) == 1:
        link = link_for_key(model._dry_key_column(), model)
        if link is not None:
            item['_links'] = link
    for column, foreign_model in model.get_links():
        link = link_for_key(column, foreign_model)
        if link is not None:
            item[column] = {column: item[column],
                            '_links': link}
    for column, (foreign_model, _) in model.get_relationships():
        if column in item:
            for x in item[column]:
                convert_links_for_item(x, foreign_model,
                                       add_top_self_link=True)

@step('list_to_dict', 'output_list,top_model,output', 'output')
def list_to_dict(context):
    r'''Converts the list in `output_list` into an `output` dict.

    We never want to return a top-level json list to the client, due to security
    vulnerabilities in older browsers.

    Stores the `output_list` in `output._response`.

    Sorts the list by the key columns so that hashed etags always get the
    same answer for the same data.
    '''
    output_list = context.output_list
    if output_list:
        keys = context.top_model._dry_primary_keys
        def get_keys(obj):
            r'''Translates id: {'id': xx, '_links': ...} into xx.
            '''
            ans = []
            for key in keys:
                key_value = obj.get(key)
                if key_value is not None:
                    if isinstance(key_value, dict):
                        ans.append(key_value[key])
                    else:
                        ans.append(key_value)
            if len(output_list) > 1:
                assert ans
            return ans
        print("list_to_dict, keys:", keys)
        print("list_to_dict, first key", get_keys(output_list[0]))
        output_list = sorted(output_list, key=get_keys)
    context.output['_response'] = output_list

@if_needed('to_json', 'output', 'output_bytes')
def to_json(context):
    context.output_bytes = \
      json.dumps(context.output, **json_settings).encode('utf-8')

@step('get_versions', 'output_bytes', 'etag')
def generate_sha1_etag(context):
    hash = hashlib.sha1()
    hash.update(context.output_bytes)
    context.etag = hash.hexdigest()

@if_needed('set_final_versions', 'last_modified,etag',
           'final_last_modified,final_etag')
def set_final_versions(context):
    r'''Copies last_modified/etag to final_last_modified/final_etag.
    '''
    context.final_last_modified = context.last_modified
    context.final_etag = context.etag

@step('add_version_headers', 'final_last_modified,final_etag,headers',
      'headers')
def add_version_headers(context):
    context.headers = _add_version_headers(context.final_last_modified,
                                           context.final_etag,
                                           context.headers)

def _add_version_headers(last_modified, etag, headers=None):
    if headers is None:
        headers = {}
    if last_modified is not None:
        headers['Last-Modified'] = datetime_to_header_format(last_modified)
    headers['ETag'] = '"{}"'.format(etag)
    return headers

@step('add_general_links',
      'relation_category,authorization_context,output,cache_public',
      'output.2,cache_public')
def add_general_links(context):
    rc_links, public = links.get_relation_category_links(
                         context.relation_category,
                         context.authorization_context)
    add_links(context.output, rc_links)
    if not public:
        context.cache_public = False

@if_needed('set_known_keys', 'url_parameters', 'known_keys')
def set_known_keys_from_url_parameters(context):
    context.known_keys = context.url_parameters.copy()

@if_needed('set_known_keys', 'item,model', 'known_keys')
def set_known_keys_from_item(context):
    item = context.item
    model = context.model
    context.known_keys = {model.__name__.lower() + '_id' if col == 'id'
                                                         else col
                            : getattr(item, col)
                          for col in model._dry_primary_keys}

@step('add_specific_links',
      'known_keys,authorization_context,output,cache_public',
      'output.2,cache_public')
def add_specific_links(context):
    specific_links, public = links.get_keyed_links(
                               context.known_keys,
                               context.authorization_context)
    add_links(context.output, specific_links)
    if not public:
        context.cache_public = False

def add_links(output, links):
    r'''Merges links into output['_links'].
    '''
    if links:
        if '_links' not in output:
            output['_links'] = {}
        _links = output['_links']
        for rc, relations in links.items():
            if rc not in _links:
                _links[rc] = {}
            for relation, url in relations.items():
                if relation in _links[rc]:
                    abort(500, debug="duplicate linke: {}.{}"
                                       .format(rc, relation))
                _links[rc][relation] = url

@step('add_cache_headers', 'cache_public,cache_max_age,headers', 'headers.2')
def add_cache_headers(context):
    context.headers.update(cache(context.cache_max_age, context.cache_public))

@step('add_location_header', 'model,item,headers', 'headers')
def add_location_header(context):
    r'''Only used in post to report the location of the newly created item.
    '''
    context.headers['Location'] = \
      context.model.item_resource.url_for_item(context.item)

@step('create_response', 'output,output_bytes,status,headers', 'response')
def create_response(context):
    if context.output_bytes is not None:
        context.headers['Content-Type'] = 'application/json'
        context.response = make_response(context.output_bytes, context.status,
                                         context.headers)
    else:
        output = context.output
        if not output:
            context.response = make_response('', context.status,
                                             context.headers)
        else:
            context.response = output, context.status, context.headers


def strip_errors(errors):
    r'''Strip lists of empty dicts from child errors lists.

        >>> strip_errors({'a': [defaultdict(list), defaultdict(list)],
        ...               'b': ['no', 'way'],
        ...               'c': []})
        {'b': ['no', 'way']}
    '''
    if errors is None:
        return None
    ans = errors.copy()
    for k, v in errors.items():
        if not v:
            del ans[k]
        elif isinstance(v[0], defaultdict):
            v = strip_errors_list(v)
            if v is None:
                del ans[k]
            else:
                ans[k] = v
    return ans

def strip_errors_list(errors_list):
    v = [strip_errors(x) for x in errors_list]
    if not any(v):
        return None
    return v

def strip_revised(revised):
    r'''Strip lists of empty dicts from child revised lists.

        >>> strip_revised({'a': [{}, {}, {}], 'b': 42, 'c': []})
        {'b': 42}
    '''
    if revised is None:
        return None
    ans = revised.copy()
    for k, v in revised.items():
        if isinstance(v, (list, tuple)):
            v = strip_revised_list(v)
            if v is None:
                del ans[k]
            else:
                ans[k] = v
    return ans

def strip_revised_list(revised_list):
    v = [strip_revised(x) for x in revised_list]
    if not any(v):
        return None
    return v

def as_datetime(x):
    r'''Converts x to datetime.

        >>> as_datetime('2000-01-01T12:13:14')
        datetime.datetime(2000, 1, 1, 12, 13, 14)
        >>> as_datetime('2000-01-01T12:13:14.001')
        datetime.datetime(2000, 1, 1, 12, 13, 14, 1000)
    '''
    if x is None or isinstance(x, datetime):
        return x
    if '.' in x:
        return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f")
    return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")

def as_date(x):
    r'''Converts x to date.

        >>> as_date('2000-01-01')
        datetime.date(2000, 1, 1)
    '''
    if x is None or isinstance(x, date):
        return x
    y, m, d = x.split('-')
    return date(int(y), int(m), int(d))

def as_time(x):
    r'''Converts x to time.

        >>> as_time('12:13:14')
        datetime.time(12, 13, 14)
        >>> as_time('12:13:14.001')
        datetime.time(12, 13, 14, 1000)
    '''
    if x is None or isinstance(x, time):
        return x
    if '.' in x:
        x, u = x.split('.')
        u = int(u + '0' * (6 - len(u)))
    else:
        u = 0
    h, m, s = x.split(':')
    return time(int(h), int(m), int(s), u)
