# http_methods.py

r'''Template :class:`.attrs` for each http method.
'''

from copy import deepcopy

from .class_init import attrs, extend, remove
from .steps import *

__all__ = (
    'post_method', 'post_authenticated_method', 'post_create_method',
      'post_item_method',
    'get_method', 'get_item_method', 'get_list_method',
    'get_update_metadata_method', 'get_create_metadata_method',
    'put_method', 'put_item_method',
    'delete_method', 'delete_item_method',
)

post_method = attrs(
    status = 204,  # NO CONTENT
    step_fns = (
        json_content_type,
        no_conditionals,
        init_errors,
        report_errors,
        create_response,
    ),
)

post_authenticated_method = deepcopy(post_method)
post_authenticated_method.step_fns = extend(
    check_csrf,
   #create_authorization_context,
    authorize,
)

post_create_method = deepcopy(post_authenticated_method)
post_create_method.status = 201   # CREATED
post_create_method.step_fns = extend(
   #create_authorization_context,
    get_new_item,
   #create_item,
   #add_specific_links,
    add_general_links,
    add_location_header,
)

post_item_method = deepcopy(post_create_method)
post_item_method.step_fns = extend(
   #create_authorization_context,
    get_insert_item_columns,
    validate_new_columns,
    validate_insert,
    create_item,
    set_known_keys_from_item,
    add_specific_links,
)

get_method = attrs(
    status = 200,  # OK
    step_fns = (
       #create_authorization_context,
        authorize,
        no_content,
        check_get_conditionals,
        accepts_json,
        set_final_versions,
        add_version_headers,
        add_cache_headers,
        add_general_links,
        create_response,
    ),
)

get_list_method = deepcopy(get_method)
get_list_method.no_query_parameters_ok = False
get_list_method.column_auth_method = 'column_auth_for_list'
get_list_method.provided_attributes = extend('column_auth_method')
get_list_method.step_fns = extend(
   #create_authorization_context,
    get_query,
    get_list,
    filter_list_columns,
    convert_list_links,
    list_to_dict,
    to_json,
    generate_sha1_etag,
    set_final_versions,
)

get_partial_list_method = deepcopy(get_list_method)
get_partial_list_method.no_query_parameters_ok = True
get_partial_list_method.step_fns = extend(
   #create_authorization_context,
    get_auth_item,
    query_list,
    set_known_keys_from_url_parameters,
    add_specific_links,
)

get_item_method = deepcopy(get_method)
get_item_method.column_auth_method = 'column_auth_for_get'
get_item_method.provided_attributes = extend('column_auth_method')
get_item_method.step_fns = extend(
   #create_authorization_context,
    get_key_columns,
    get_item,
    get_item_versions,
    filter_item_columns,
    convert_item_links,
    set_known_keys_from_url_parameters,
    add_specific_links,
)

get_update_metadata_method = deepcopy(get_item_method)
get_update_metadata_method.column_auth_method = 'column_auth_for_update'
get_update_metadata_method.metadata_type = 'update'
get_update_metadata_method.step_fns = remove(
   #get_key_columns,
    get_item,
    get_item_versions,
   #filter_item_columns,
    convert_item_links,
   #add_version_headers,
   #add_specific_links,
)
get_update_metadata_method.step_fns = extend(
   #no_conditionals,
    get_auth_item,
    load_column_info,
    create_metadata,
    to_json,
    generate_sha1_etag,
    set_final_versions,
)

get_update_list_metadata_method = deepcopy(get_update_metadata_method)
get_update_list_metadata_method.step_fns = remove(
    get_key_columns,
    get_item,
)
get_update_list_metadata_method.step_fns = extend(
    get_auth_item,
)

get_create_metadata_method = deepcopy(get_update_metadata_method)
get_create_metadata_method.column_auth_method = 'column_auth_for_insert'
get_create_metadata_method.metadata_type = 'create'
get_create_metadata_method.step_fns = remove(
    get_key_columns,
    get_item,
    set_known_keys_from_url_parameters,
    add_specific_links,
)

put_method = attrs(
    status = 204,  # NO CONTENT
    step_fns = (
        get_new_item,
       #create_authorization_context,
        authorize,
        json_content_type,
       #get_item,
        check_csrf,
        init_errors,
        validate_update,
       #update_item,
        report_errors,
        add_version_headers,
        create_response,
    ),
)

put_item_method = deepcopy(put_method)
put_item_method.step_fns = extend(
   #create_authorization_context,
    get_key_columns,
    check_update_conditionals,
    get_item,
    get_item_versions,
    get_updated_item_columns,
    abort_no_updates,
    validate_updated_columns,
    update_item,
)

put_list_method = deepcopy(put_method)
put_list_method.step_fns = extend(
    get_auth_item,
   #create_authorization_context,
    get_query,
    query_list,
    get_list,
    list_to_dict,
    to_json,
    generate_sha1_etag,
    set_final_versions,
    check_update_conditionals,
    get_new_list,
    init_list_errors,
    get_updated_list_columns,
    abort_no_list_updates,
    validate_updated_columns_in_list,
    validate_updates_in_list,
    update_list,
)

delete_method = attrs(
    status = 204,  # NO CONTENT
    step_fns = (
       #create_authorization_context,
        authorize,
        no_content,
       #get_item,
       #get_item_versions,
        check_csrf,
       #delete_item,
        create_response,
    ),
)

delete_item_method = deepcopy(delete_method)
delete_item_method.step_fns = extend(
   #create_authorization_context,
    get_key_columns,
    get_item,
    get_item_versions,
    check_update_conditionals,
    delete_item,
)
