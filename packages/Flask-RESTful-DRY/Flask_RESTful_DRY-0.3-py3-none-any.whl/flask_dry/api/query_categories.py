# query_categories.py

from sqlalchemy.sql.expression import or_
from flask.ext.restful import abort

from .steps import step
from .class_init import attrs as attrs_cls
from .links import register_link


__all__ = ('query_category', 'query', 'multi_arg_query', 'query_columns',
           'query_any',
          )


class query_category(attrs_cls):
    r'''Query_categories are collections of queries that can be combined.

    The individual queries can be accessed by their rel type or their q_param.
    '''
    def __init__(self, queries, **attrs):
        attrs_cls.__init__(self, **attrs)
        self._queries = {}
        for q in queries:
            if q.q_param in self._queries:
                raise ValueError("duplicate queries for q_param {}"
                                 .format(q.q_param))
            self._queries[q.q_param] = q

    def __repr__(self):
        return "<query_category {}>".format(self._queries.values())

    def does(self, q_params):
        r'''Which q_params in `q_params` can this query_category do?

        Returns the set of q_params from `q_params` that this query_category
        can do.

        `q_params` is a set (or frozenset) of q_param names.
        '''
        return q_params.intersection(self._queries)

    def prepare_context(self, context, args):
        self.copy_into(context)
        for name, arg in args.items():
            self._queries[name].prepare_context(context, arg,
                                                self._filter_position)
    
    def compile(self, app, context):
        self.copy_into(context)
        context.location += '.' + str(self)
        context.step__placeholder = placeholder
        steps = context.compile_steps(context.trace, context.trace_final,
                                      context.show_unused_steps)
        filter_position = steps.index(placeholder)
        self.steps = steps[:filter_position] + steps[filter_position + 1:]
        self._filter_position = filter_position
        self.register_links(app, context)

    def register_links(self, app, context):
        r'''Generates the links for all of the queries in the query_category.

        These are tuples of (relation_category, relation, url).
        '''
        for q in self._queries.values():
            q.register_link(app, context)

@step('placeholder', 'query', 'query')
def placeholder(context):
    r'''Marks where filters should go in the compiled steps list.
    '''
    pass

def get_query_category(query_categories, q_params):
    r'''Returns the query_category for q_params.

    Returns None if there are no q_params.

    Aborts with 400 if the q_params don't match, or match more than one
    query_category.
    '''
    if not q_params:
        return None

    query_categories = [qc for qc in query_categories
                           if qc.does(q_params)]

    if len(query_categories) > 1:
        combinations = sorted(sorted(qc.does(q_params))
                              for qc in query_categories)
        abort(400, message="illegal combination of query parameters: {}"
                             .format(' with '.join(' or '.join(c)
                                                   for c in combinations)))

    unknown_params = q_params
    for qc in query_categories:
        unknown_params -= qc.does(q_params)
    if unknown_params:
        abort(400, message="illegal query parameter: {}"
                             .format(' and '.join(sorted(unknown_params))))

    return query_categories[0]  # sole query_category


class query:
    r'''Base class for individual url query parameter processors.

    The derived class must define a filter method to add the SQLAlchemy filter
    elements to the SQLAlchemy query object.

    These add the query parameter argument(s) to the context.
    '''
    _args = ()

    def __init__(self, relation, q_param=None):
        if relation is not None:
            self.relation = relation
        if q_param:
            self.q_param = q_param
        else:
            self.q_param = self.relation

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    def get_query_arg(self, context, arg_name='arg'):
        return getattr(context, "{}_{}".format(self.relation, arg_name))

    def prepare_context(self, context, arg, filter_position):
        self.store_arg(context, arg)
        context.steps = context.steps[:filter_position] + (self.filter,) + \
                        context.steps[filter_position:]

    def store_arg(self, context, arg):
        setattr(context, "{}_arg".format(self.relation),
                self.translate_arg(arg))

    def translate_arg(self, arg):
        r'''Override this if you don't want a Python str value.
        '''
        return arg

    @property
    def query_template(self):
        r'''The url query syntax to append to the collection url.
        '''
        return '?{}={}'.format(self.q_param,
                               ','.join('{{{}}}'.format(arg)
                                        for arg in self._args))

    def register_link(self, app, context):
        register_link(app, context.keys, context.relation_category,
                      self.relation, context.url_format + self.query_template,
                      context.authorization_requirements)

class multi_arg_query(query):
    r'''Set self._args to the names of the arguments.
    '''
    def store_arg(self, context, arg):
        args = arg.split(',')
        if not args or len(args) != len(self._args):
            abort(400, message="Invalid number of arguments to {}: "
                               "expected {}, got {}"
                               .format(self.q_param, len(self._args), arg))
        for arg_name, raw_arg in zip(self._args, args):
            setattr(context, "{}_{}".format(self.relation, arg_name),
                    self.translate_arg(raw_arg, arg_name))

    def translate_arg(self, arg, argument_name):
        r'''Override this in subclass if you don't want strings.
        '''
        return arg


class query_columns(multi_arg_query):
    r'''Takes comma separated values for named (multi-)column queries.

    Multiple columns are comma separated in url query string:

        ?q_param=column1,column2,column3,...

    Also works for single column queries.
    '''
    def __init__(self, relation, q_param=None, columns=None):
        multi_arg_query.__init__(self, relation, q_param)
        if columns:
            self._args = columns
        else:
            self._args = (self.q_param,)

    def filter(self, context):
        context.query = context.query.filter_by(
                          **{column: self.get_query_arg(context, column)
                             for column in self._args})


class query_any(query):
    r'''Searches for one value in any of a number of columns.
    '''
    def __init__(self, relation, q_param=None, columns=None):
        query.__init__(self, relation, q_param)
        self._args = (self.q_param,)
        self._columns = columns

    def filter(self, context):
        query_arg = self.get_query_arg(context)
        model = context.model
        context.query = context.query.filter(
                          or_(*[getattr(model, column) == query_arg
                                for column in self._columns]))

