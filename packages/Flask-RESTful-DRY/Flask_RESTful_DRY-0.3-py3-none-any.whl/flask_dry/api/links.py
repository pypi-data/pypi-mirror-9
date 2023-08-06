# links.py

r'''Global link registry.

Links are registered at program startup.  First, they need a flask app:

    >>> from .app import DRY_Flask
    >>> current_app = DRY_Flask(__name__)  # overrides import for testing

And some authorization requirements:

    >>> from .authorization import Requirement, Base_auth_context
    >>> class Test_requirement(Requirement):
    ...     def validate(self, context, debug):
    ...         return self.role == context.role
    >>> admin_role = Test_requirement(role='admin')
    >>> user_role = Test_requirement(role='user')

And authorization contexts:

    >>> class Auth_context(Base_auth_context):
    ...     def __init__(self, role):
    ...         Base_auth_context.__init__(self)
    ...         self.role = role
    >>> admin_context = Auth_context('admin')
    >>> user_context = Auth_context('user')
    >>> other_context = Auth_context('other')

Now we can register 5 links:

    >>> register_link(current_app, (), 'rc1', 'r1.1', 'url1.1', ())
    >>> register_link(current_app, (), 'rc1', 'r1.2', 'url1.2', (admin_role,))
    >>> register_link(current_app, (), 'rc2', 'r2.1', 'url2.1', (user_role,))
    >>> register_link(current_app, ('a',), 'rc3', 'r3.1', 'url3.1/{a}',
    ...               ())
    >>> register_link(current_app, ('a', 'b'), 'rc4', 'r4.1', 'url4.1/{a}/{b}',
    ...               (admin_role, user_role))

Which can be looked up en-mass as needed:

    >>> from pprint import pprint
    >>> with current_app.app_context():
    ...     pprint(get_relation_category_links('rc1', other_context))
    ({'rc1': {'r1.1': 'url1.1'}}, False)
    >>> with current_app.app_context():
    ...     pprint(get_relation_category_links('rc1', admin_context))
    ({'rc1': {'r1.1': 'url1.1', 'r1.2': 'url1.2'}}, False)
    >>> with current_app.app_context():
    ...     pprint(get_keyed_links(dict(a='a_value'), other_context))
    ({'rc3': {'r3.1': 'url3.1/a_value'}}, True)
    >>> with current_app.app_context():
    ...     pprint(get_keyed_links(dict(a='a_value', b='b_value', c='c_value'),
    ...                            other_context))
    ({'rc3': {'r3.1': 'url3.1/a_value'}}, False)
    >>> with current_app.app_context():
    ...     pprint(get_keyed_links(dict(a='a_value', b='b_value', c='c_value'),
    ...                            admin_context))
    ({'rc3': {'r3.1': 'url3.1/a_value'},
      'rc4': {'r4.1': 'url4.1/a_value/b_value'}},
     False)
'''

from itertools import chain, combinations, groupby
from operator import itemgetter

from flask import current_app

from .authorization import Anybody


def register_link(app, keys, relation_category, relation, url_format,
                  authorization_requirements):
    # Condense requirements
    requirements = []
    for r in authorization_requirements:
        if isinstance(r, Anybody):
            requirements = []
            break
        if not any(r.equivalent(r2) for r2 in requirements):
            requirements.append(r)

    if not keys:
        app.dry_relation_category_links[relation_category].append(
          (relation, url_format, tuple(requirements)))
    else:
        app.dry_keyed_links[tuple(sorted(keys))].append(
          (relation_category, relation, url_format, tuple(requirements)))

def get_relation_category_links(relation_category, auth_context):
    r'''Returns {relation_category: {relation: url}}, cache_public.
    '''
    links, cache_public = _filter(
      current_app.dry_relation_category_links[relation_category],
      auth_context)
    if links:
        return {relation_category: dict(links)}, cache_public
    return {}, cache_public

def get_all_relation_category_links(auth_context):
    r'''Returns {relation_category: {relation: url}}, cache_public.
    '''
    cache_public = True
    all_rc_links = {}
    for rc in current_app.dry_relation_category_links.keys():
        rc_links, public = get_relation_category_links(rc, auth_context)
        all_rc_links.update(rc_links)
        if not public:
            cache_public = False
    return all_rc_links, cache_public

def get_keyed_links(keys, auth_context):
    r'''Returns {relation_category: {relation: url}}, cache_public.

    Grabs all subsets of keys.  Substitutes the key values into the urls.

    `keys` is {key_name: key_value}.
    '''
    auth_links, cache_public = _filter(
      chain.from_iterable(current_app.dry_keyed_links[tuple(sorted(subset))]
                          for subset in powerset(keys.keys())),
      auth_context)
    return ({relation_category: {relation: url_format.format(**keys)
                                 for _, relation, url_format in links}
             for relation_category, links
              in groupby(sorted(auth_links, key=itemgetter(0)),
                         key=itemgetter(0))},
            cache_public)

def _filter(links, auth_context):
    r'''Returns authorized links, cache_public.
    '''
    auth_links = []
    cache_public = True
    for *link, requirements in links:
        if requirements:
            cache_public = False
            if any(auth_context.meets(r, debug=False) for r in requirements):
                auth_links.append(link)
        else:
            auth_links.append(link)
    return auth_links, cache_public

# From itertools recipes, modified to not generate the empty sequence.
def powerset(iterable):
    r'''
        >>> tuple(powerset([1,2,3]))
        ((1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3))
    '''
    s = tuple(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

