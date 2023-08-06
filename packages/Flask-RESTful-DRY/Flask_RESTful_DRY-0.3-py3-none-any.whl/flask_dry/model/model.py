# model.py

r'''This has the :class:`.Model` class.

To be used rather than the db.Model_ in Flask-SQLAlchemy_.

.. _db.Model: https://pythonhosted.org/Flask-SQLAlchemy/api.html#flask.ext.sqlalchemy.Model
.. _Flask-SQLAlchemy: https://pythonhosted.org/Flask-SQLAlchemy/
'''

import sys
from itertools import chain

from sqlalchemy import util, text
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSON, All, Any, array
from sqlalchemy.exc import DataError, IntegrityError

from flask.ext.login import current_user

from .column_info import Column_info
from .utils import db, lookup_model, get_current_user_id
from .translate_errors import translate_error


__all__ = ('text', 'db', 'Model',

           # SQLAlchemy postgresql extensions:
           'ARRAY', 'ENUM', 'JSON', 'All', 'Any', 'array',
          )


@compiles(DateTime, 'postgresql')
def _compile_datetime(element, compiler, **kw):
    r'''To avoid round-off problems datetimes in HTTP headers.

    Datetimes in HTTP headers have no fractional seconds.
    '''
    return "TIMESTAMP(0) WITHOUT TIME ZONE"


class Model(db.Model):
    r'''Use this as the base class to define your "models" (i.e., database
    tables).
    '''
    __abstract__ = True

    @classmethod
    def _dry_key_column(cls):
        assert len(cls._dry_primary_keys) == 1, \
               "Can only handle 1 primary key, not {}" \
                 .format(len(cls._dry_primary_keys))
        return cls._dry_primary_keys[0]

    @classmethod
    def keys(cls):
        return chain(cls._dry_column_info.keys(), cls._dry_relationships.keys())

    def items(self):
        return [(name, getattr(self, name)) for name in self.keys()]

    @classmethod
    def dry_get_column_info(cls, column):
        return cls._dry_column_info[column]

    @classmethod
    def get_links(cls):
        return cls._dry_links.items()

    @classmethod
    def get_relationships(cls):
        return cls._dry_relationships.items()

    @classmethod
    def _dry_register(cls):
        #print("register", cls.__name__)
        cls._dry_links = {}                       # col_name: foreign_model
        cls._dry_relationships = {}               # col_name: (foreign_model,
                                                  #            reverse_column)
        cls._dry_primary_keys = []                # [col_name]
        cls._dry_column_info = {}                 # col_name: Column_info
        cls._dry_relation_categories = set()      # {relation_category_name}
        for name, value in util.iterate_attributes(cls):
            if isinstance(value, InstrumentedAttribute):
                prop = value.property
                if isinstance(prop, ColumnProperty):
                    assert len(prop.columns) == 1, \
                           "name {}, len {}".format(name, len(prop.columns))
                    cls._dry_column_info[name] = \
                      Column_info(cls, name, prop.columns[0])
                elif isinstance(prop, RelationshipProperty):
                    assert prop.local_remote_pairs
                    if len(prop.local_remote_pairs) > 1:
                        # FIX: What to do about many-to-many relationships?
                        for x in prop.local_remote_pairs:
                            print("local_remote_pair", x)
                        #   '{}.{}: Multicolumn relationships not supported' \
                        #     .format(cls.__name__, name)
                    else:
                        local, remote = prop.local_remote_pairs[0]
                        #print("remote name", remote.name)
                        #print("relationship", dir(prop))
                        #print("backref", prop.backref)
                        #print("back_populates", prop.back_populates)
                        #print("class_attribute", prop.class_attribute)
                        #print("collection_class", prop.collection_class)
                        #print("comparator", prop.comparator)
                        #print("compare", prop.compare)
                        #print("direction", prop.direction)
                        #print("distinct_target_key", prop.distinct_target_key)
                        #print("key", prop.key)
                        #print("local_columns", prop.local_columns)
                        #print("local_remote_pairs", prop.local_remote_pairs)
                        #print("table", prop.table)
                        #print("target", prop.target)
                        #print("uselist", prop.uselist)
                        cls._dry_relationships[name] = (
                          lookup_model(prop.table.name),
                          remote.name)
        #if cls._dry_links:
        #    print("_dry_links", cls._dry_links)
        #if cls._dry_relationships:
        #    print("_dry_relationships", cls._dry_relationships)

    def dry_cross_validate(self, now, revised, errors):
        r'''Checks interdependencies between columns.

        This occurs after validate_insert/validate_update and after `self` has
        been updated, just before writing it to the database.

        Does not validate child objects.
        '''
        pass

    @classmethod
    def dry_relationships(cls):
        r'''Generates col_name, (foreign_model, reverse_column)
        '''
        return cls._dry_relationships.items()

    def check_database_errors(self, errors):
        r'''Flush updates to database and check for errors.
        '''
        try:
            db.session.flush()
        except (DataError, IntegrityError) as e:
            for column, message in translate_error(e):
                errors[column].append(message)
            db.session.rollback()

    @classmethod
    def get_query(cls):
        r'''Override this in subclasses to filter out rows flagged as deleted.
        '''
        return cls.query

    @classmethod
    def validate_insert(cls, context, new_item, role, now, errors, revised):
        r'''Validates new_item before it's inserted into the database.

        `new_item` is an :class:`.new_item` object.

        May update system_updated_attributes in `new_item`.

        Does not validate child objects in new_item.

        Derived classes should override this as needed.

        Does not return anything.
        '''
        col_info = cls._dry_column_info
        if 'created_timestamp' in col_info:
            new_item.add_system_updated_attribute('created_timestamp', now)
        if 'created_by' in col_info:
            new_item.add_system_updated_attribute('created_by',
                                                  get_current_user_id())
        if 'last_modified_timestamp' in col_info:
            new_item.add_system_updated_attribute('last_modified_timestamp',
                                                  now)
        if 'last_modified_by' in col_info:
            new_item.add_system_updated_attribute('last_modified_by', 
                                                  get_current_user_id())

    def validate_update(self, context, updated_columns, role, now, errors,
                        revised):
        r'''Validates `updated_columns` against `self`.
        
        This occurs before `self` is updated.

        `updated_columns` is an :class:`.updated_item` object.

        May update system_updated_attributes in `updated_columns`.

        Does not validate child objects in new_item.

        Derived classes should override this as needed.

        Does not return anything.
        '''
        col_info = self._dry_column_info
        if 'last_modified_timestamp' in col_info:
            updated_columns.add_system_updated_attribute(
              'last_modified_timestamp', now)
        if 'last_modified_by' in col_info:
            updated_columns.add_system_updated_attribute(
              'last_modified_by', get_current_user_id())
        if 'etag' in col_info:
            updated_columns.add_system_updated_attribute(
              'etag', self.etag + 1)

    def dry_delete(self, now):
        r'''Deletes this row.

        Override in subclasses to set flags on deletion.
        '''
        db.session.delete(self)

    @classmethod
    def get_status(cls, key):
        r'''Returns 404 NOT FOUND if key > sequence for this model,

        else 410 GONE.
        '''
        assert len(cls._dry_primary_keys) == 1
        pkey = cls._dry_primary_keys[0]
        seq = cls._dry_column_info[pkey].sequence
        if seq is not None:
            conn = db.session.connection().connection
            cur = conn.cursor()
            try:
                cur.execute('SELECT nextval({!r})'.format(seq))
                nextval = cur.fetchone()[0]
            except conn.Error as e:
                print("SELECT nextval({!r})".format(seq), "failed with",
                      repr(e))
                #pass
            else:
                #print(cls.__name__, "get_status nextval", nextval, "key", key)
                if nextval > key:
                    return 410
            finally:
                cur.close()
        return 404

