# app.py

r'''This is where the DRY_Flask app class is declared.
'''

import sys
from collections import defaultdict

from sqlalchemy.event import listen
from sqlalchemy.orm import mapper, configure_mappers
from flask import Flask, request_finished, session, current_app
from flask.sessions import SecureCookieSessionInterface
from flask.wrappers import Response

from ..model.utils import db, names_from_module


class DRY_Response(Response):
    default_mimetype = None


class DRY_Flask(Flask):
    response_class = DRY_Response

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # {(key, ...):
        #    [(relation_category, relation, url_format, requirements)]}
        self.dry_keyed_links = defaultdict(list)

        # {relation_category: [(relation, url, requirements)]}
        self.dry_relation_category_links = defaultdict(list)

        if self.testing:
            # This lets us manufacture session cookies for testing...

            print("WARNING: Using Insecure session cookies for testing",
                  file=sys.stderr)

            def serialize(data):
                r'''Serialize session data.

                Format is space separated key:value pairs.
                '''
                assert isinstance(data, dict)
                return ' '.join("{}:{}".format(k, s(v))
                                for k, v in sorted(data.items()))

            def deserialize(data):
                r'''Deserialize serialized session data.
                '''
                def de_kv(kv):
                    k, v = kv.split(':')
                    return k, d(v)
                return dict(de_kv(kv) for kv in data.split(' '))

            def s(v):
                r'''Serialize a value.
                '''
                return repr(v)

            def d(v):
                r'''Deserialize a serialized value.

                Wasn't brave (foolish?) enough to use "eval" here...
                '''
                if v[0] == "'":
                    return v[1:-1]
                try:
                    return float(v)
                except ValueError:
                    try:
                        return int(v)
                    except ValueError:
                        return bool(v)

            class InsecureSessionInterface(SecureCookieSessionInterface):
                override_header = 'X-Session'
                def open_session(self, app, request):
                    if self.override_header not in request.headers:
                        print("open_session deferring to super")
                        return super().open_session(app, request)
                    val = request.headers.get(self.override_header)
                    print("open_session got", repr(val))
                    if not val:
                        return self.session_class()
                    try:
                        data = deserialize(val)
                    except ValueError:
                        return self.session_class()
                    print("open_session deserialized", data)
                    return self.session_class(data)

            self.session_interface = InsecureSessionInterface()

            def dump_session(app, response):
                print("final session:")
                for k, v in sorted(session.items()):
                    print("    {}: {!r}".format(k, v))

            request_finished.connect(dump_session)

    def load_models_from_module(self, all_models):
        r'''Takes a module that has imported all of models.
        
        Returns {model.__name__: model}
        '''
        #print("load_models_from_module")
        return self.load_models(*names_from_module(all_models))

    def load_models(self, *models):
        r'''Loads models into the app.
        '''
        db.init_app(self)
        self.dry_unique_constraints = {}
        self.dry_foreign_key_constraints = {}
        self.dry_models_by_tablename = {}
        models_map = {}
        for model in models:
            self.dry_models_by_tablename[model.__tablename__] = model
            models_map[model.__name__] = model
        listen(mapper, "after_configured", self._register)
        with self.app_context():
            # FIX: Does this break when multiple apps use flask_dry?
            configure_mappers()  # calls self._register, below
        return models_map

    def _register(self):
        #print("register models ************************************")
        for model in self.dry_models_by_tablename.values():
            model._dry_register()
        #print("done register models ************************************")

