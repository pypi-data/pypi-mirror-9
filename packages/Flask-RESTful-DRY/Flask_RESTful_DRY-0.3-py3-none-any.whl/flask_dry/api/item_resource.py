# item_resource.py

from .class_init import extend, attrs, lookup
from .dry_resource import DRY_Resource
from . import http_methods
from .utils import get_universal


def init_self(cls, url_dummies, dummy_path):
    if cls.put_method is not None:
        cls.url_classes = ('metadata_update',)

    # Set columns_to_keys
    if len(cls.keys) == 1:
        if len(cls.model._dry_primary_keys) != 1:
            raise AssertionError(
                    "Number of primary keys, {}, does not match "
                    "single url_parameter, {}"
                    .format(len(cls.model._dry_primary_keys), cls.keys))
        cls.columns_to_keys = \
          {cls.model._dry_primary_keys[0]: cls.keys[0]}
    else:
        if sorted(cls.model._dry_primary_keys) != sorted(cls.keys):
            raise AssertionError(
                    "Multiple primary keys {} do not match "
                    "url_parameters {}"
                    .format(sorted(cls.model._dry_primary_keys),
                            sorted(cls.keys)))
        cls.columns_to_keys = {k: k for k in cls.keys}

def init_collection(cls, url_dummies, dummy_path):
    if cls.post_method is not None:
        cls.url_classes = ('metadata_create',)

    # Set keys from "self" relation to None in "collection" for the various
    # create authorization context steps.
    for k in cls.resource_class.relations['self'].keys:
        setattr(cls, k, None)

def init_metadata_update(cls, url_dummies, dummy_path):
    # Give metadata the same authorization_requirements as the post/put
    # methods:
    pm = url_dummies.get('self', {}).get('put_method')
    if pm is not None:
        cls.get_method.authorization_requirements = \
          pm.authorization_requirements

def init_metadata_create(cls, url_dummies, dummy_path):
    # Give metadata the same authorization_requirements as the post/put
    # methods:
    pm = url_dummies.get('collection', {}).get('post_method')
    if pm is not None:
        cls.get_method.authorization_requirements = \
          pm.authorization_requirements


class Item_Resource(DRY_Resource):
    url_classes = extend('self', 'collection')

    # Default HTTP methods
    post_item_method = http_methods.post_item_method
    get_item_method = http_methods.get_item_method
    put_item_method = http_methods.put_item_method
    delete_item_method = http_methods.delete_item_method
    get_create_metadata_method = http_methods.get_create_metadata_method
    get_update_metadata_method = http_methods.get_update_metadata_method
    get_list_method = http_methods.get_list_method

    # Overrides for "self" url class:
    self = attrs(
        get_method=lookup('get_item_method'),
        put_method=lookup('put_item_method'),
        delete_method=lookup('delete_item_method'),
        post_method=None,
        init_fn = init_self,
        provided_attributes = extend('columns_to_keys')
    )

    self.metadata_update = attrs(
        url_extension = '/metadata',
        get_method = lookup('get_update_metadata_method'),
        put_method = None,
        post_method = None,
        delete_method = None,
        init_fn = init_metadata_update,
    )

    # Overrides for "collection" url class:
    collection = attrs(
        url_extension = '',  # FIX: Should this be '/'?
        auth_item = None,
        provided_attributes = extend('auth_item'),
        get_method = lookup('get_list_method'),
        post_method = lookup('post_item_method'),
        put_method = None,
        delete_method = None,
        init_fn = init_collection,
    )

    collection.metadata_create = attrs(
        url_extension = '/metadata',
        get_method = lookup('get_create_metadata_method'),
        put_method = None,
        post_method = None,
        delete_method = None,
        init_fn = init_metadata_create,
    )

    @classmethod
    def resource_init(cls, api):
        url_dummies = super().resource_init(api)

        # Store the item_resource on the model
        cls.model.item_resource = cls

        return url_dummies

    @classmethod
    def create_url_classes(cls, resource_class, api, url_dummies, dummy_path=(),
                           base_url_class=None):
        if not hasattr(cls.self, 'url_extension'):
            cls.self.url_extension = \
              '/<int:{}_id>'.format(cls.model.__name__.lower())

        super().create_url_classes(resource_class, api, url_dummies, dummy_path,
                                   base_url_class)

    @classmethod
    def url_for_item(cls, item):
        self = cls.relations['self']
        return self.url_format.format(
                 **{key: get_universal(item, column)
                    for column, key in self.columns_to_keys.items()})

    @classmethod
    def link_for_key(cls, key):
        r'''Returns {relation: url}.
        '''
        self = cls.relations['self']
        assert len(self.keys) == 1
        return {self.relation: self.url_format.format(**{self.keys[0]: key})}
