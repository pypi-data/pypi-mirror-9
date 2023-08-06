# utils.py

from datetime import datetime, timedelta

from flask import request


# e.g.: Wed, 15 Nov 1995 14:58:08 GMT
_last_modified_datetime_format = '%a, %d %b %Y %H:%M:%S GMT'


def cache(max_age, public):
    r'''Returns a dict of caching headers.
    '''
    # no-cache can include headers to exclude?  (e.g., Set-Cookie)
    if max_age:
        expires = datetime.utcnow() + timedelta(seconds=max_age)
    else:
        expires = datetime.utcnow() - timedelta(hours=1)
    return {'Cache-Control':
              "max_age={}, {}".format(max_age, "public" if public
                                                        else "private"),
            'Expires':
              datetime_to_header_format(expires),
           }


def datetime_to_header_format(dt):
    r'''Converts a datetime into http header format.

    Assumes that the datetime is already in UTC.

        >>> dt = datetime(2014, 10, 11, 12, 13, 14)
        >>> datetime_to_header_format(dt)
        'Sat, 11 Oct 2014 12:13:14 GMT'
    '''
    return dt.strftime(_last_modified_datetime_format)


def get_universal(obj, attr, default=None):
    r'''Gets attr from obj.

    Works for both dicts and objects.

    Also accepts None for `obj`, which always returns `default`.
    '''
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def external_url(url_path, **format_args):
    full_url = "{}/{}".format(request.host_url.rstrip('/'),
                              url_path.lstrip('/'))
    if format_args:
        return full_url.format(**format_args)
    return full_url
