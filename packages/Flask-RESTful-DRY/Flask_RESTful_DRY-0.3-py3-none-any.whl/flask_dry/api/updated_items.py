# updated_items.py

import sys
from collections import defaultdict
from itertools import chain


class system_attributes:
    r'''Records system updated attributes on an item.

    System updated attributes are set by the system and bypass validation.
    Examples are last_modified_timestamp and etag.
    '''
    def __init__(self, model, sublists):
        self._model = model
        self._sublists = sublists
        self._system_updated_attributes = {}

    def add_system_updated_attribute(self, key, value):
        assert key not in self._system_updated_attributes
        self._system_updated_attributes[key] = value

    def system_updated_attributes(self):
        r'''Generates key, value pairs for system_updated_attributes.
        '''
        return self._system_updated_attributes.items()

    def sublists(self):
        r'''Generates key, sublist pairs for sublists.
        '''
        return self._sublists.items()

    def get_sublist(self, column):
        r'''Returns the :class:`.updated_list` for sublist `column`.
        '''
        return self._sublists[column]


class new_item(system_attributes):
    r'''A new_item must be INSERT-ed into the database.

    All of the supplied attributes are considered user updated attributes.
    '''
    _status = 'new'

    def __init__(self, model, new_item, sublists):
        system_attributes.__init__(self, model, sublists)
        self._user_updated_attributes = new_item

    def __repr__(self):
        return "<new_item: {}>".format(self._model.__name__)

    def __getattr__(self, key):
        r'''This does not provide access to system_updated_attributes.
        '''
        if key.startswith('_'):
            raise AttributeError("{!r} object has no attribute {!r}"
                                   .format(self.__class__.__name__, key))
        try:
            return self._user_updated_attributes[key]
        except KeyError:
            raise AttributeError("New {!r} object has no attribute {!r}"
                                   .format(self._model.__name__, key)) \
                  from None

    def __delattr__(self, key):
        r'''This does not provide access to system_updated_attributes.
        '''
        del self._user_updated_attributes[key]

    def __setattr__(self, key, value):
        r'''This does not provide access to system_updated_attributes.
        '''
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self._user_updated_attributes[key] = value

    def attr_changed(self, attr):
        return (attr in self._user_updated_attributes or
                attr in self._system_updated_attributes)

    def user_updated_attributes(self):
        r'''Generates key, value pairs for user_updated_attributes.
        '''
        return self._user_updated_attributes.items()

    def updated_attributes(self):
        r'''Generates key, value pairs for all updated attributes.
        '''
        return chain(self._user_updated_attributes.items(),
                     self._system_updated_attributes.items())


class updated_item(new_item):
    def __init__(self, model, updated_attributes, old_item, sublists):
        new_item.__init__(self, model, updated_attributes, sublists)
        self._old_item = old_item

    def __repr__(self):
        keys = ', '.join("{}={}".format(key, getattr(self._old_item, key))
                         for key in self._model._dry_primary_keys)
        updated_attrs = tuple(self._user_updated_attributes.keys()) + \
                        tuple(key for key, sl in self._sublists.items()
                                  if sl._status != 'unchanged')
        return "<updated_item: {}={{{}}} updated {}>".format(
                 self._model.__name__, keys, updated_attrs)

    @property
    def _status(self):
        if self._user_updated_attributes or self._system_updated_attributes:
            return 'updated'
        return 'unchanged'

    def __getattr__(self, key):
        r'''This does not provide access to system_updated_attributes.
        '''
        try:
            return super().__getattr__(key)
        except AttributeError:
            return getattr(self._old_item, key)


class deleted_item:
    _status = 'deleted'

    def __init__(self, model, old_item):
        self._model = model
        self._old_item = old_item

    def __repr__(self):
        keys = ', '.join("{}={}".format(key, getattr(self._old_item, key))
                         for key in self._model._dry_primary_keys)
        return "<deleted_item: {}={{{}}}>".format(self._model.__name__, keys)

    def __getattr__(self, key):
        if key.startswith('_'):
            raise AttributeError("{!r} object has no attribute {!r}"
                                   .format(self.__class__.__name__, key))
        return getattr(self._old_item, key)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            raise AssertionError("May not change attributes on deleted_item")

    def __delattr__(self, key):
        raise AssertionError("May not delete attributes on deleted_item")


class updated_list:
    r'''Tracks changes to a list of items.

      * self.updated_items is a list of :class:`.updated_item`,
        :class:`.new_item`, and :class:`.deleted_item` objects.

      * self.user_list is the list of items as submitted by the user.

      * self.old_list is the current list of items in the database.
    '''
    def __init__(self, model, parent_link_column, updated_items, user_list,
                 old_list):
        self.model = model
        self.parent_link_column = parent_link_column
        self.updated_items = updated_items
        self.user_list = user_list
        self.old_list = old_list

    @property
    def _status(self):
        if any(ua._status != 'unchanged' for ua in self.updated_items):
            return 'updated'
        return 'unchanged'

    def get_by_status(self, status):
        r'''Generates updated_items that match `status`.
        '''
        return filter(lambda ua: ua._status == status, self.updated_items)


def make_updated_item(model, user_item, old_item, errors, action_column_auth):
    r'''Returns a new_item or updated_item.

    Compares user_item to old_item to see what changed.  If old_item is None,
    it returns a new_item, otherwise an updated_item.

    Also reports attempted changes to unauthorized `columns` in `errors`.

    The user_item is not referenced by the returned object, so is not later
    updated.  But the old_item _is_ referenced by the returned object and is
    generally updated later when it is updated in the database.

    This also handles nested children.  Consider:

        >>> from ..model.model import *
        >>> from ..model.columns import *
        >>> class Grandchild(Model):
        ...     __tablename__ = 'grandchildren'
        ...     id = Id()
        ...     a = PlainString()
        ...     b = PlainString()
        ...     nope = PlainString()
        ...     child = DRY_Column(db.Integer, db.ForeignKey('children.id'))
        >>> class Child(Model):
        ...     __tablename__ = 'children'
        ...     id = Id()
        ...     c = PlainString()
        ...     d = PlainString()
        ...     grandchildren = db.relationship('Grandchild')
        ...     top = DRY_Column(db.Integer, db.ForeignKey('tops.id'))
        >>> class Top(Model):
        ...     __tablename__ = 'tops'
        ...     id = Id()
        ...     e = PlainString()
        ...     f = PlainString()
        ...     children = db.relationship('Child')

    We'll create an app and load these into the app:

        >>> from .app import DRY_Flask
        >>> app = DRY_Flask(__name__)
        >>> _ = app.load_models(Grandchild, Child, Top)

    Then with a context for Top:

        >>> from .allow import Allow
        >>> from unittest.mock import Mock
        >>> context = Mock(update_column_suffixes=('update_columns',),
        ...                insert_column_suffixes=('insert_columns',),
        ...                update_columns=Allow('e', 'f'),
        ...                children__update_columns=Allow('c', 'd'),
        ...                children__grandchildren__update_columns=
        ...                  Allow('a', 'b'),
        ...                children__grandchildren__insert_columns=
        ...                  Allow('a'),
        ...               )

    And a user_item:

        >>> user_item = dict(id=1, e='e', f='f1',
        ...                  children=[dict(id=2, c='c', d='d2', w='unknown',
        ...                                 grandchildren=[
        ...                                   dict(id=3, a='a3', b='b3',
        ...                                        nope='unauthorized'),
        ...                                   dict(id=4, a='a4', b='b',
        ...                                        nope='nope4'),
        ...                                   dict(a='a6', b='b6'),
        ...                                 ])])

    Against an old_item:

        >>> old_item = Top(id=1, e='e1', f='f1',
        ...                children=[Child(id=2, c='c2', d='d2',
        ...                                grandchildren=[
        ...                                  Grandchild(id=3, a='a3', b='b3',
        ...                                             nope='nope3'),
        ...                                  Grandchild(id=4, a='a4', b='b4',
        ...                                             nope='nope4'),
        ...                                  Grandchild(id=5, a='a5', b='b5',
        ...                                             nope='nope5'),
        ...                                ])])

    Then, calling make_updated_item:

        >>> errors = defaultdict(list)
        >>> from .column_auth import item_column_auth
        >>> item_authorizer = item_column_auth(context)
        >>> action_authorizer = item_authorizer.get_update_column_auth()
        >>> ua = make_updated_item(Top, user_item, old_item, errors,
        ...                        action_authorizer)

    We get these errors:

        >>> isinstance(errors, defaultdict)
        True
        >>> sorted(errors.keys())
        ['children']
        >>> len(errors['children'])
        1
        >>> child_errors = errors['children'][0]
        >>> isinstance(child_errors, defaultdict)
        True
        >>> sorted(child_errors.keys())
        ['grandchildren', 'w']
        >>> child_errors['w']
        ['Unknown field']
        >>> grandchildren_errors = child_errors['grandchildren']
        >>> len(grandchildren_errors)
        3
        >>> all(isinstance(c, defaultdict) for c in grandchildren_errors)
        True
        >>> grandchildren_errors == [{'nope': ['Unauthorized']},
        ...                          {},
        ...                          {'b': ['Unauthorized']}]
        True

    And this result:

        >>> ua
        <updated_item: Top={id=1} updated ('e', 'children')>
        >>> ua._status
        'updated'
        >>> sorted(ua.system_updated_attributes())
        []
        >>> sorted(ua.user_updated_attributes())
        [('e', 'e')]
        >>> sorted(key for key, value in ua.sublists())
        ['children']
        >>> sl = ua.get_sublist('children')
        >>> sl._status
        'updated'
        >>> sl.updated_items
        [<updated_item: Child={id=2} updated ('c', 'grandchildren')>]
        >>> [u._index for u in sl.updated_items]
        [0]
        >>> sorted(sl.updated_items[0].system_updated_attributes())
        [('top', 1)]
        >>> sorted(key for key, value in sl.updated_items[0].sublists())
        ['grandchildren']
        >>> gc = sl.updated_items[0].get_sublist('grandchildren')
        >>> gc._status
        'updated'
        >>> gc.updated_items
        [<updated_item: Grandchild={id=3} updated ()>, <updated_item: Grandchild={id=4} updated ('b',)>, <new_item: Grandchild>, <deleted_item: Grandchild={id=5}>]
        >>> [u._status for u in gc.updated_items]
        ['unchanged', 'updated', 'new', 'deleted']
        >>> [sorted(u.system_updated_attributes())
        ...  for u in gc.updated_items[:-1]]
        [[], [('child', 2)], [('child', 2)]]
        >>> [u._index for u in gc.updated_items[:-1]]
        [0, 1, 2]
        >>> gc.updated_items[-1]._index
        Traceback (most recent call last):
        ...
        AttributeError: 'deleted_item' object has no attribute '_index'
    '''
    denied = action_column_auth.denied(user_item.keys())
    key_column = model._dry_key_column()  # of parent
    key = getattr(old_item, key_column) if old_item is not None else None
    updated_columns = {}  # {column_name: user_value}
    sublists = {}         # {column_name: updated_list}
    column_info = model._dry_column_info
    relationships = model._dry_relationships

    for new_column, new_value in user_item.items():
        if new_column in column_info:
            if old_item is None or new_value != getattr(old_item, new_column):
                # User changed this column!
                if new_column in denied:
                    print("Attempted change to unauthorized column", new_column,
                          "in", model.__name__, file=sys.stderr)
                    errors[new_column].append("Unauthorized")
                else:
                    updated_columns[new_column] = new_value
        elif new_column in relationships:
            list_errors = [defaultdict(list) for _ in range(len(new_value))]
            child_model, parent_link_column = relationships[new_column]
            sublists[new_column] = make_sublist(
                                     child_model,
                                     new_value,
                                     () if old_item is None
                                        else getattr(old_item, new_column),
                                     list_errors,
                                     action_column_auth.get_sublist_column_auth(
                                       new_column
                                     ),
                                     parent_link_column,
                                     key)
            errors[new_column] = list_errors
        else:
            errors[new_column].append("Unknown field")

    if old_item is None:
        return new_item(model, updated_columns, sublists)

    return updated_item(model, updated_columns, old_item, sublists)


def make_sublist(model, user_list, old_list, list_errors, item_column_auth,
                 parent_link_column, parent_key=None):
    r'''Returns an updated_list.

    The user_list is not referenced or later updated by the returned
    updated_list.  But the old_list _is_ referenced by the returned
    updated_list and will generally be updated later when the old_items are
    updated in the database.
    '''

    # Figure out key_column, the name of the column that uniquely identifies
    # the child in this list.
    primary_keys = model._dry_primary_keys
    if len(primary_keys) == 1:
        # Expect a system-generated id field which is different than
        # parent_link_column.
        key_column = primary_keys[0]
        assert parent_link_column != key_column
    else:
        # Expect a pair of foreign keys, with one of them being
        # parent_link_column.
        assert len(primary_keys) == 2
        print("primary_keys", primary_keys, file=sys.stderr)
        key_column = primary_keys[1 - primary_keys.index(parent_link_column)]

    # Index old items.  These are deleted as found, leaving the items to
    # delete.
    old_items = {getattr(item, key_column): item
                 for item in old_list}

    sublist = []

    # Add everything in user_list to sublist
    for i, user_item in enumerate(user_list):
        # Existing item, or new item?
        if key_column in user_item:
            # Existing item
            item_key = user_item[key_column]
            if item_key not in old_items:
                list_errors[i][key_column].append("Unknown child id")
                continue
            # Updated item
            updated_item = make_updated_item(model, user_item,
                                             old_items[item_key],
                                             list_errors[i],
                                             item_column_auth
                                               .get_update_column_auth())
            del old_items[item_key]
        else:
            # New item
            updated_item = make_updated_item(model, user_item, None,
                                             list_errors[i],
                                             item_column_auth
                                               .get_insert_column_auth())
        updated_item._index = i
        if updated_item._status != 'unchanged' and parent_key is not None:
            # Check parent_link_column and set it if not present:
            user_parent_key = getattr(updated_item, parent_link_column, None)
            #print("item", i, "user_parent_key", user_parent_key)
            if user_parent_key is None:
                updated_item.add_system_updated_attribute(parent_link_column,
                                                          parent_key)
            elif user_parent_key != parent_key:
                list_errors[i][parent_link_column].append("Incorrect parent id")
        sublist.append(updated_item)

    # Convert remaining old_items to deleted_items on sublist.
    sublist.extend(deleted_item(model, old_item)
                   for old_item in old_items.values())

    return updated_list(model, parent_link_column, sublist, user_list, old_list)

