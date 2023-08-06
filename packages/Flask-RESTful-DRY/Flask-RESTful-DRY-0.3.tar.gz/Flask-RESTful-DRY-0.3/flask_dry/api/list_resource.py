# list_resource.py

from .class_init import extend, attrs, lookup
from .dry_resource import DRY_Resource
from . import http_methods


def init_list_url_classes(cls, url_dummies, dummy_path):
    if cls.put_method is not None:
        cls.url_classes = ('metadata_update',)

class List_Resource(DRY_Resource):
    url_classes = extend('list')

    # Default HTTP methods
    get_partial_list_method = http_methods.get_partial_list_method
    put_list_method = http_methods.put_list_method
    get_update_list_metadata_method = \
      http_methods.get_update_list_metadata_method

    # Overrides for "self" url class:
    list = attrs(
        url_extension = '',
        get_method=lookup('get_partial_list_method'),
        put_method=lookup('put_list_method'),
        delete_method=None,
        post_method=None,
        init_fn = init_list_url_classes,
    )

    list.metadata_update = attrs(
        url_extension = '/metadata',
        get_method = lookup('get_update_list_metadata_method'),
        put_method = None,
        post_method = None,
        delete_method = None,
    )

    @classmethod
    def resource_init(cls, api):
        if not hasattr(cls, 'relation_category'):
            cls.relation_category = cls.__name__.lower()
        if not hasattr(cls, 'resource_extension'):
            cls.resource_extension = \
              '/{}/<int:{}_id>'.format(cls.relation_category,
                                       cls.__name__.split('_')[0].lower())
        url_dummies = super().resource_init(api)

        # Give metadata the same authorization_requirements as the post/put
        # methods:
        if 'metadata_update' in cls.relations:
            pm = url_dummies.get('list', {}).get('put_method')
            if pm is not None:
                cls.relations['metadata_update'].get_method \
                   .authorization_requirements = \
                url_dummies['list']['metadata_update']['get_method'] \
                   .authorization_requirements = \
                  pm.authorization_requirements

        return url_dummies

