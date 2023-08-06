# api.py

from datetime import datetime, date, time

from flask.ext.restful import Api
from flask.ext.restful.representations import json

from ..model.utils import names_from_module


_datetime_formats = {
    datetime: '%Y-%m-%dT%H:%M:%S',
    date: '%Y-%m-%d',
    time: '%H:%M:%S',
}

def to_json(o):
    format = _datetime_formats.get(type(o))
    if format:
        return o.strftime(format)
    #print("to_json can't do", repr(o))
    raise TypeError

json.settings.update(sort_keys=True,
                     ensure_ascii=False,
                     check_circular=False,
                     default=to_json,
                    )

class DRY_Api(Api):
    def __init__(self, app=None, *args, **kwargs):
        if app is not None and app.debug:
            json.settings.setdefault('indent', 4)
        kwargs.setdefault('catch_all_404s', True)
        super().__init__(app, *args, **kwargs)

    def load_apis_from_module(self, all_apis):
        #print("load_apis_from_module")
        return self.load_apis(*names_from_module(all_apis))

    def load_apis(self, *apis):
        #print("load_apis")
        apis = {}
        for each_api in apis:
            if hasattr(each_api, 'resource_init'):
                each_api.resource_init(self)
            apis[each_api.__name__] = each_api
        return apis

    def unauthorized(self, response):
        if 'WWW-Authenticate' not in response.headers:
            response.headers['WWW-Authenticate'] = \
              'login realm="{}"'.format(
                self.app.config['DRY_WWW_AUTHENTICATE_LOGIN_REALM'])
        return response

