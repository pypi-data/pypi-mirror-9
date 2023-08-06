# step_utils.py

r'''These are the functions to support defining steps.

Each step has a step name.  Each step name may have several implementations
(functions) to choose from.  At most one of these implementations may be chosen
for each HTTP method.

Each implementation has a list of needs (names) and a list of what it provides
that other steps might need.  The steps that provide what another step needs
are prerequisites of that step.  This imposes a partial ordering over the
steps execution.

In addition, a few steps have a milestone number.  These steps are executed in
increasing milestone number, doing all of their prerequisite steps first.

After the final milestone step is executed, the steps needed to provide the
'response' attribute are executed.  Thus, not all steps need to be tied to a
milestone.
'''

import sys
from collections import defaultdict
from functools import wraps, partial
from itertools import groupby, tee, filterfalse, chain
from operator import itemgetter, attrgetter, lt, le, gt
from pprint import PrettyPrinter
from inspect import signature, Parameter


__all__ = ('step', 'if_needed', 'parameterize',
          )


Steps = []

def step(name=None, needs='', provides='', milestone=None, optional=False):
    r'''Function decorator for step functions.

    You can only use one step of each `name` in any context.  But the different
    implementations of the same `name` may have different `needs`, `provides`,
    and `milestones`.  A missing name gets replaced by a unique name when the
    steps are built.

    The steps are run in increasing `milestone`.  It is permissable to use
    multiple steps with the same `milestone`.  In this case, they are run in an
    arbitrary order relative to each other.

    It is also OK if no step provides a need.  These are silently ignored.
    The assumption is that it will become obvious the first time you run the
    code, and it is good to document all of the needs.

    It is also OK if multiple steps provide the same attribute.  In this case,
    all of these steps will be run before any step than needs that attribute.

    Cycles are not allowed, except that steps may need and provide the same
    attribute.  This indicates that they modify that attribute.  In this case,
    they will be executed _after_ steps that provide the attribute, but don't
    need it (i.e., steps that create the attribute).
    '''
    def decorate(fn):
        fn.step_name = name and 'step__' + name
        fn.needs = make_tuple(needs)
        fn.provides = make_tuple(provides)
        fn.milestone = milestone
        fn.optional = optional
        Steps.append(fn)
        return fn
    #return decorate
    return lambda fn: trace(decorate(fn))

def if_needed(name=None, needs='', provides=''):
    needs_versions, provides_versions, _, _ = \
      _assign_versions(make_tuple(needs), make_tuple(provides))
    assert any(needs_versions.get(p) != v
               for p, v in provides_versions.items()), \
           "if_needed step has no created attributes"
    return step(name, needs, provides, optional=True)

def make_tuple(names):
    if isinstance(names, tuple):
        return names
    if not names.strip():
        return ()
    return tuple(name.strip() for name in names.split(','))

pprint = PrettyPrinter(indent=1, width=80, depth=2, compact=True).pprint

def trace(fn):
    @wraps(fn)
    def surrogate(*args, context, **kwds):
        if context.debug:
            if fn.needs:
                print("step", fn.__name__, "got:")
                for need in fn.needs:
                    print(' ', need)
                    print('    ', end='')
                    pprint(getattr(context, need.split('.')[0], '<not-set>'))
            else:
                print("step", fn.__name__)
        fn(context=context, *args, **kwds)
        if context.debug:
            if fn.provides:
                print("step", fn.__name__, "provided:")
                for p in fn.provides:
                    print(' ', p)
                    print('    ', end='')
                    pprint(getattr(context, p, '<not-set>'))
            else:
                print("step", fn.__name__, "done")
            print()
    surrogate.step_name = fn.step_name
    surrogate.needs = fn.needs
    surrogate.provides = fn.provides
    surrogate.milestone = fn.milestone
    surrogate.optional = fn.optional
    return surrogate

# This is probably a bad idea.  Parameters can be passed in the context, which
# makes it easier to standardize the steps in one place.
#
# But, this can customize the needs/provides lists!  So maybe it's not a bad
# idea?
def parameterize(fn):
    def make_partial(*args, **kwargs):
        sig = signature(fn)
        ba = sig.bind_partial(*args, **kwargs)
        for param in sig.parameters.values():
            if param.name not in ba.arguments and \
               param.default is not Parameter.empty:
                ba.arguments[param.name] = param.default

        p = partial(fn, *ba.args, **ba.kwargs)
        p.__name__ = fn.__name__
        p.step_name = fn.step_name
        p.needs = update_tuple(fn.__name__, fn.needs, ba.arguments)
        p.provides = update_tuple(fn.__name__, fn.provides, ba.arguments)
        p.milestone = fn.milestone
        p.optional = fn.optional
        return p
    return make_partial

def update_tuple(fn_name, t, args):
    r'''Returns a new tuple based on `t`, but modified by `args`.

    The result is a copy of `t` with values from `args` substituted for
    corresponding values in `t`.

    `args` is a dict of {parameter_name: value} for the parameters passed in
    the parameterize call.  If the parameter_name appears in `t`, the value is
    substituted for the parameter_name in the result.  If the value is a string
    containing ',' or a list or tuple, all of the values are added to the
    result.  If the value is a dict, all of its keys are added to the result.

    Parameter_names appearing in `t` are not allowed to have .n suffix.

    Also modifies the values of `args` to strip any .n suffix because the
    attribute in the context doesn't contain these suffixes.
    '''
    ans = []
    for x in t:
        base = x.split('.')[0]
        if base not in args:
            ans.append(x)
        else:
            assert base == x, \
              '.n suffix not allowed on parameterized argument {} to {}' \
                .format(x, fn_name)
            new_x = args[base]
            if isinstance(new_x, str) and ',' in new_x:
                new_x = make_tuple(new_x)
            if isinstance(new_x, (list, tuple)):
                ans.extend(new_x)
                args[base] = tuple(y.split('.')[0] for y in new_x)
            elif isinstance(new_x, dict):
                ans.extend(new_x.keys())
                args[base] = {k.split('.')[0]: v for k, v in new_x.items()}
            else:
                ans.append(new_x)
                args[base] = new_x.split('.')[0]
    return tuple(ans)


def all_attrs(steps=None):
    if steps is None:
        steps = Steps
    return sorted(set(chain.from_iterable(chain(step.needs, step.provides)
                                          for step in steps)))

def steps_using(need, f=sys.stdout):
    print("providing", sorted(steps_providing(need)), file=f)
    print("updating", sorted(steps_updating(need)), file=f)
    print("needing", sorted(steps_needing(need)), file=f)


def dump_attr_map():
    from . import steps
    with open("attr_map", "wt") as f:
        for attr in all_attrs():
            print("{}:".format(attr), file=f)
            steps_using(attr, f)
            print(file=f)

def steps_providing(need):
    r'''`need` in step.provides, but not in step.needs.
    '''
    return tuple((step.__name__ if step.milestone is None
                                else "{}({})".format(step.__name__,
                                                     step.milestone))
                 for step in Steps
                 if need in [n.split('.')[0] for n in step.provides] and
                    need not in [n.split('.')[0] for n in step.needs])


def steps_updating(need):
    r'''`need` in step.needs and step.provides.
    '''
    return tuple((step.__name__ if step.milestone is None
                                else "{}({})".format(step.__name__,
                                                     step.milestone))
                 for step in Steps
                 if need in [n.split('.')[0] for n in step.needs] and
                    need in [n.split('.')[0] for n in step.provides])


def steps_needing(need):
    r'''`need` in step.needs, but not in step.provides.
    '''
    return tuple((step.__name__ if step.milestone is None
                                else "{}({})".format(step.__name__,
                                                     step.milestone))
                 for step in Steps
                 if need in [n.split('.')[0] for n in step.needs] and
                    need not in [n.split('.')[0] for n in step.provides])


def generate_provides_map(context, steps):
    r'''Gather what steps provide what.

    Returns {provided_attribute: (primary_steps, secondary_steps)}

    The steps for each provided attribute are partitioned into two lists:
    primary and secondary.  The primary steps set the attribute (do not need
    it, or that version), while the secondary steps update the attribute (i.e.,
    also need the same version).

    Each of the primary_steps and secondary_steps are lists of (version,
    [step]) in increasing version order.  The primary_steps only have one step
    in their list unless the name of the provided_attribute starts with an '_'.

    So, given the following steps:

        >>> from unittest.mock import Mock
        >>> def __repr__(self): return self.__name__
        >>> step1 = Mock(__name__ = 'step1', optional=False, __repr__=__repr__,
        ...              needs=('a', 'c'), provides=('a', 'b'))
        >>> step2 = Mock(__name__ = 'step2', optional=False, __repr__=__repr__,
        ...              needs=('b',), provides=('a', 'b'))
        >>> step3 = Mock(__name__ = 'step3', optional=False, __repr__=__repr__,
        ...              needs=('a', 'b'), provides=('a', 'b'))

    And a context that shows what we're doing:

        >>> context = Mock(url_class_name='url_class_name', location='location')

    The resulting provides_map is:

        >>> provides_map = generate_provides_map(context, (step1, step2, step3))
        >>> sorted(provides_map.keys())
        ['a', 'b']
        >>> provides_map['a']
        ([(1, [step2])], [(1, [step1, step3])])
        >>> provides_map['b']
        ([(1, [step1])], [(1, [step2, step3])])

    Multiple required creators for the same attributes is an error:

        >>> step1 = Mock(__name__ = 'step1', optional=False, __repr__=__repr__,
        ...              needs=(), provides=('a',))
        >>> step2 = Mock(__name__ = 'step2', optional=False, __repr__=__repr__,
        ...              needs=(), provides=('a',))
        >>> generate_provides_map(context, (step1, step2))
        Traceback (most recent call last):
        ...
        AssertionError: url_class_name.location: duplicate required steps creating 'a': step1 and step2

    Multiple optional creators for the same attributes is also an error:

        >>> step1 = Mock(__name__ = 'step1', optional=True, __repr__=__repr__,
        ...              needs=(), provides=('a',))
        >>> step2 = Mock(__name__ = 'step2', optional=True, __repr__=__repr__,
        ...              needs=(), provides=('a',))
        >>> generate_provides_map(context, (step1, step2))
        Traceback (most recent call last):
        ...
        AssertionError: url_class_name.location: duplicate optional steps creating 'a': step1 and step2

    But a required creator silently wins out over an optional one:

        >>> step1 = Mock(__name__ = 'step1', optional=False, __repr__=__repr__,
        ...              needs=(), provides=('a',))
        >>> step2 = Mock(__name__ = 'step2', optional=True, __repr__=__repr__,
        ...              needs=(), provides=('a',))
        >>> generate_provides_map(context, (step1, step2))['a']
        ([(1, [step1])], [])

    Regardless of which one appears first:

        >>> step1 = Mock(__name__ = 'step1', optional=True, __repr__=__repr__,
        ...              needs=(), provides=('a',))
        >>> step2 = Mock(__name__ = 'step2', optional=False, __repr__=__repr__,
        ...              needs=(), provides=('a',))
        >>> generate_provides_map(context, (step1, step2))['a']
        ([(1, [step2])], [])

    Steps with a needs version > the provided version are illegal:

        >>> step1 = Mock(__name__ = 'step1', optional=True, __repr__=__repr__,
        ...              needs=('a.2',), provides=('a.1',))
        >>> generate_provides_map(context, (step1,))
        Traceback (most recent call last):
        ...
        AssertionError: step 'step1', attr 'a': needed version must be <= provided version
    '''
    ans = defaultdict(lambda: (defaultdict(list), defaultdict(list)))
    for step in steps:
        needs, provides, _, _ = assign_versions(step)
        for p, v in provides.items():
            if p in needs and v <= needs[p]:
                # This step updates p
                assert v == needs[p], (
                       "step {!r}, attr {!r}: "
                         "needed version must be <= provided version"
                         .format(step.__name__, p))
                ans[p][1][v].append(step)
            elif p.startswith('_'):
                ans[p][0][v].append(step)
            else:
                # This step creates p
                p_steps = ans[p][0][v]  # previous step creating p (or [])
                if not p_steps:
                    p_steps.append(step)
                elif p_steps[0].optional:
                    if step.optional:
                        raise AssertionError(
                                "{}.{}: duplicate optional steps "
                                "creating {!r}: {} and {}"
                                  .format(context.url_class_name,
                                          context.location, p,
                                          p_steps[0].__name__, step.__name__))
                    else:
                        # replace optional step with required one
                        p_steps[0] = step
                elif not step.optional:
                    raise AssertionError(
                            "{}.{}: duplicate required steps creating {!r}: "
                            "{} and {}"
                              .format(context.url_class_name, context.location,
                                      p, p_steps[0].__name__, step.__name__))

    return {attr: (sorted(p.items()), sorted(s.items()))
            for attr, (p, s) in ans.items()}


def assign_versions(step):
    r'''Assigns versions to all needs and provides in `step`.

    Returns needs, provides, needs_order, provides_order.  The needs and
    provides are both {attr: version}.  The two orders are just tuples of attr
    names (without the .version suffix) in the order that they appear in the
    step.

    If no version is provided for a need without a matching provides, the
    version is set to 99.

    If an attribute appears in both the needs and provides, and one doesn't
    have a version, it is assigned the version of the other.  If neither have
    a version, they are both assigned version 1.

    If no version is provided for a provides without a matching needs, the
    version is set to 1.

        >>> from unittest.mock import Mock
        >>> step = Mock(needs=['a', 'b.2', 'c', 'd', 'e.4'],
        ...             provides=['c', 'd.2', 'e', 'g.3', 'f'])
        >>> needs, provides, needs_order, provides_order = assign_versions(step)
        >>> sorted(needs.items())
        [('a', 99), ('b', 2), ('c', 1), ('d', 2), ('e', 4)]
        >>> sorted(provides.items())
        [('c', 1), ('d', 2), ('e', 4), ('f', 1), ('g', 3)]
        >>> needs_order
        ('a', 'b', 'c', 'd', 'e')
        >>> provides_order
        ('c', 'd', 'e', 'g', 'f')
    '''
    return _assign_versions(step.needs, step.provides)


def _assign_versions(needs, provides):
    needs, needs_order = split_versions(needs)
    provides, provides_order = split_versions(provides)
    for n, _ in filter(lambda item: item[1] is None, needs.items()):
        if n not in provides:
            needs[n] = 99
        else:
            pv = provides[n]
            if pv is None:
                needs[n] = provides[n] = 1
            else:
                needs[n] = pv
    for p, _ in filter(lambda item: item[1] is None, provides.items()):
        if p not in needs:
            provides[p] = 1
        else:
            provides[p] = needs[p]
    return needs, provides, needs_order, provides_order


def split_versions(attrs):
    r'''Splits the versions from the attr names in attrs.

    Returns {attr_name: version}, attr_order where version is None if omitted.
    Attr_order is just a tuple of attr names in the order provided, without
    any .version suffix.

        >>> map, order = split_versions(('a', 'b.4'))
        >>> sorted(map.items())
        [('a', None), ('b', 4)]
        >>> order
        ('a', 'b')
    '''
    version_dict = {}
    order = []
    for a in attrs:
        if '.' in a:
            name, version = a.split('.')
            version_dict[name] = int(version)
            order.append(name)
        else:
            version_dict[a] = None
            order.append(a)
    return version_dict, tuple(order)


def get_milestones(steps):
    r'''Gather and sort all of the milestone steps.

    Returns a list of steps that have milestones set on them, in increasing
    milestone order.
    '''
    return sorted((step for step in steps
                        if getattr(step, 'milestone', None) is not None),
                  key=attrgetter('milestone'))


def get_unprovided_needs():
    r'''Returns unprovided needs, examining all `Steps`.
    '''
    # FIX: This will fail with duplicate steps creating the same attribute.
    provided = {attr
                for attr, (primary, secondary)
                 in generate_provides_map(None, Steps).items()
                if primary}
    return {need for step in Steps
                 for need in step.needs
                 if need[0] != '_' and need.split('.')[0] not in provided}


def generate_prerequisites(context, steps, provides_map):
    r'''Generates prerequisites for steps.

    Returns {successor: [(predecessor, reason)]}, {unneeded_optional_step}

    `provides_map` is {provided_need: (primary_steps, secondary_steps)}
    where primary_steps and secondary_steps are sorted lists of (version,
    [step]).

    If provides_map has 'response', this also includes the predecessors to
    response.99 under the key 'response' in the answer.

    If any needed attribute has no primary_steps to create it, and is not
    listed in the context.provided_attributes, an AssertionError is raised.

    The rules are:

        N.n: consumes N.n
          - after all P.q and N.xP.q where q <= n
          - before all P.q and N.xP.q where q > n
        N.nP.p(n<p): consumes N.n, changes it to P.p
          - after all P.q and N.xP.q where q <= n
        N.nP.n: updates N.n
          - after all P.q and N.xP.q(x<q) where q <= n
          - after all N.qP.q where q < n
        N.nP.p(n>p): illegal, already eliminated in generate_provides_map
        P.p: creates P
          - after all P.q and N.xP.q where q < p 

    So,

        >>> from unittest.mock import Mock
        >>> context = Mock("context", provided_attributes=())
        >>> def __repr__(self): return self.__name__
        >>> step1 = Mock(__name__='step1', __repr__=__repr__,
        ...              needs=(), provides=('a',), optional=True)
        >>> step2 = Mock(__name__='step2', __repr__=__repr__,
        ...              needs=('a',), provides=('a',), optional=False)
        >>> step3 = Mock(__name__='step3', __repr__=__repr__,
        ...              needs=('a.1',), provides=('a.2',), optional=True)
        >>> step4 = Mock(__name__='step4', __repr__=__repr__,
        ...              needs=('a.2',), provides=('b'), optional=True)
        >>> provides_map = dict(a=([(1, [step1]), (2, [step3])],
        ...                        [(1, [step2])]),
        ...                     b=([(1, [step4])], []))
        >>> prereqs, unneeded_steps = \
        ...   generate_prerequisites(context, (step1, step2, step3, step4),
        ...                          provides_map)
        >>> for rule in sorted(prereqs.items(), key=lambda r: r[0].__name__):
        ...    print("{0[0]}: {0[1]}".format(rule))
        step2: [(step1, 'for a.1 needed by step2')]
        step3: [(step1, 'for a.1 needed by step3'), (step2, 'for a.1 needed by step3')]
        step4: [(step1, 'for a.2 needed by step4'), (step3, 'for a.2 needed by step4'), (step2, 'for a.2 needed by step4')]
        >>> unneeded_steps
        {step4}
    '''
    prereqs = defaultdict(list)
    optional_steps = set()
    needed_steps = set()

    def after(s, providers, cmp_fn, v, reason):
        r'''`s` comes after `providers` for `reason`.

        Only applies to `providers` meeting `cmp_fn` against `v`.
        '''
        for pv, provider_steps in filter(lambda item: cmp_fn(item[0], v),
                                         providers):
            #print(s, "after", provider_steps)
            for step in provider_steps:
                prereqs[s].append((step, reason))

    def before(s, providers, cmp_fn, v, n):
        r'''`s` comes before `providers`.

        Only applies to `providers` meeting `cmp_fn` against `v`.
        '''
        for pv, provider_steps in filter(lambda item: cmp_fn(item[0], v),
                                         providers):
            #print(s, "before", provider_steps)
            for successor in provider_steps:
                prereqs[successor].append(
                  (s, "before {} produces {}.{}"
                        .format(successor.__name__, n, pv)))

    for step in steps:
        if step.optional:
            optional_steps.add(step)

        # needs and provides are: {attr: version}
        needs, provides, needs_order, provides_order = assign_versions(step)

        for n in needs_order:
            primary_providers, secondary_providers = \
              provides_map.get(n, ((), ()))
            if not n.startswith('_') \
               and not primary_providers \
               and not hasattr(context, n) \
               and n not in context.provided_attributes:
                raise AssertionError(
                        "{}.{}: No step creates {!r}, needed by {}; maybe {}"
                          .format(context.url_class_name, context.location, n,
                                  step.__name__, steps_providing(n)))

            v = needs[n]
            after_reason = \
              "for {}.{} needed by {}".format(n, v, step.__name__)

            if n not in provides:
                # step consumes n
                after(step, primary_providers, le, v, after_reason)
                after(step, secondary_providers, le, v, after_reason)
                before(step, primary_providers, gt, v, n)
                before(step, secondary_providers, gt, v, n)
            elif v < provides[n]:
                # step consumes n, and creates a new version
                after(step, primary_providers, le, v, after_reason)
                after(step, secondary_providers, le, v, after_reason)
            else:
                # step updates n
                after(step, primary_providers, le, v, after_reason)
                after(step, secondary_providers, lt, v, after_reason)

            if not n.startswith('_'):
                for pv, steps in primary_providers:
                    if pv <= v:
                        needed_steps.update(steps)

        for p in provides_order:
            if p not in needs:
                primary_providers, secondary_providers = \
                  provides_map.get(p, ((), ()))
                v = provides[p]
                after_reason = \
                  "before {}.{} provided by {}".format(p, v, step.__name__)
                after(step, primary_providers, lt, v, after_reason)
                after(step, secondary_providers, lt, v, after_reason)

    # add special 'response' pseudo-step:
    if 'response' in provides_map:
        primary_providers, secondary_providers = provides_map['response']
        after('response', primary_providers, le, 99, "for final 'response'")
        after('response', secondary_providers, le, 99, "for final 'response'")

    optional_steps.difference_update(needed_steps)
    return prereqs, optional_steps


def generate_steps(context, trace=0, show_unused_steps=False):
    r'''Generates the steps to execute in the order of execution.

    Though there are generally multiple legal orderings of the steps, this
    will always generate the same ordering given the same inputs.  Thus, the
    output is completely deterministic and repeatable.

    This needs a context.

        >>> from .class_init import attrs
        >>> context = attrs(url_class_name='url_class_name',
        ...                 location='location',
        ...                 provided_attributes=('d',))

    And some steps.

        >>> class step:
        ...     def __init__(self, name, step_name=None, needs='',
        ...                  provides='', milestone=None, optional=False):
        ...         self.__name__ = name
        ...         if step_name: self.step_name = step_name
        ...         else: self.step_name = 'step__' + name
        ...         self.needs = tuple(needs)
        ...         self.provides = tuple(provides)
        ...         self.milestone = milestone
        ...         self.optional = optional
        >>> step1 = step('step1', needs='', provides='a')
        >>> step2 = step('step2', needs='a', provides='ab')
        >>> step3 = step('step3', needs='ab', provides='c', milestone=10)
        >>> step4 = step('step4', needs='d', provides='d')
        >>> step5 = step('step5', needs='db', provides='eg')
        >>> step6 = step('step6', needs='e', provides='f', milestone=20)
        >>> step7 = step('step7', None, needs='a', provides='xy')
        >>> step8 = step('step8', 'step__step2', needs='a', provides='ab')
        >>> step9 = step('step9', None, needs='y', provides=('response',))

        >>> context.step_fns = (step1, step2, step3, step4, step5, step6,
        ...                     step7, step8, step9)

    Steps can be overridden by setting them to None.

        >>> context.step__bogus = None

    Let's do it!

        >>> for fn in generate_steps(context):
        ...     print(fn.__name__)
        step1
        step8
        step3
        step4
        step5
        step6
        step7
        step9
    '''

    # Transfer step_fns to attributes:
    unique_step_number = 0
    for step_fn in context.step_fns:
        if step_fn.step_name is None:
            unique_step_number += 1
            name = 'step__{}'.format(unique_step_number)
        else:
            name = step_fn.step_name
        setattr(context, name, step_fn)

    # Gather all step functions.  These are attributes named "step__X".
    # None values are used to delete steps, so ignore None values.
    steps = sorted(filter(None, # ignore False values (i.e., None)
                          map(partial(getattr, context),
                              filter(lambda name: name.startswith('step__'),
                                     dir(context)))),
                   key=attrgetter('__name__'))

    if trace > 0:
        print("{}.{} generate_steps ++++++++++++++++++++++++++++++"
              .format(context.url_class_name, context.location))
        print("    steps", [s.__name__ for s in steps])
        with open("{}.{}.csv".format(context.url.lstrip('/').replace('/', ':'),
                                     context.location), 'wt') as f:
            attrs = sorted(frozenset([a.split('.')[0]
                                      for a in all_attrs(steps)]))
            print('', '', *attrs, sep=',', file=f)
            for step in steps:
                print(step.__name__,
                      step.milestone if step.milestone is not None
                                     else '',
                      sep=',', end='', file=f)
                needs, provides, _, _ = assign_versions(step)  # {attr: version}
                for attr in attrs:
                    if attr in needs:
                        if attr in provides:
                            print(',{}.>.{}'.format(needs[attr],
                                                    provides[attr]),
                                  end='', file=f)
                        else:
                            print(',C.{}'.format(needs[attr]), end='', file=f)
                    elif attr in provides:
                        print(',P.{}'.format(provides[attr]), end='', file=f)
                    else:
                        print(',', end='', file=f)
                print(file=f)

    # Gather what steps provide what:
    #     {provided_need: (primary_steps, secondary_steps)}
    # primary_steps and secondary_steps are sorted lists of (version, [step]).
    provides_map = generate_provides_map(context, steps)

    #  {successor: [(predecessor, reason)]}
    prereq_map, seen = generate_prerequisites(context, steps, provides_map)

    # Gather and sort all of the milestone steps:
    milestones = get_milestones(steps)

    # Generate the steps for each milestone.
    for m in milestones:
        if trace > 0:
            print("    doing milestone", m.milestone, m.__name__)
        yield from generate_step(m, context, prereq_map, seen,
                                 max_milestone=m.milestone, trace=trace,
                                 reason="as milestone {}".format(m.milestone))

    if trace > 0:
        print("    after milestones, generating providers for 'response' "
              "*******************")

    # Output steps generating 'response'
    if 'response' in prereq_map:
        yield from generate_step('response', context, prereq_map, seen,
                                 trace=trace,
                                 reason="for 'response'")

    # Output all other required steps
    for step in steps:
        if not step.optional:
            yield from generate_step(step, context, prereq_map, seen,
                                     trace=trace, reason="required")

    # Sanity check: did everything get generated?
    optional_not_used = []
    required_not_used = []
    for step in steps:
        if step not in seen:
            if step.optional:
                optional_not_used.append(step)
            else:
                required_not_used.append(step)

    if optional_not_used and show_unused_steps:
        print("{}.{}: optional steps not used:"
                .format(context.url_class_name, context.location),
              [fn.__name__ for fn in optional_not_used])
        print()
    if required_not_used:
        raise AssertionError("{}.{}: required steps not used: {}"
                             .format(context.url_class_name, context.location,
                                     [fn.__name__ for fn in required_not_used]))

def generate_step(step, context, prereq_map, seen, predecessors=(),
                  max_milestone=None, trace=0, reason=''):
    r'''Generates steps up to and including `step`.

    First generates the prerequiste steps for this step, then yields this
    step.  An exception is if step is a str, then it is not yielded.  This is
    used to generate the 'response' prerequisites.

    This needs a context.

        >>> from unittest.mock import Mock
        >>> context = Mock("context",
        ...                url_class_name='url_class_name',
        ...                location='location')

    And some steps.

        >>> step1 = Mock(__name__='step1')
        >>> step2 = Mock(__name__='step2')
        >>> step3 = Mock(__name__='step3')

    The prereq_map must be pre-computed.

        >>> prereq_map = {step1: [],
        ...               step2: [(step1, "reason 1")],
        ...               step3: [(step1, "reason 2"), (step2, "reason 3")]}

    Nothing is generated if the step has already been seen.

        >>> tuple(generate_step(step1, context, prereq_map, {step1}))
        ()

    Cycles are not allowed.

        >>> tuple(generate_step(step1, context, prereq_map, set(),
        ...                     (step2, step1, step3)))
        Traceback (most recent call last):
            ...
        AssertionError: url_class_name.location -- cycle in step_fns: (step1, step3)

    Otherwise, generate the steps!

        >>> [fn.__name__
        ...  for fn in generate_step(step1, context, prereq_map, set())]
        ['step1']

        >>> [fn.__name__
        ...  for fn in generate_step(step3, context, prereq_map, set())]
        ['step1', 'step2', 'step3']
    '''
    if step not in seen:
        if trace > 10:
            print("    generate_step",
                  (step if isinstance(step, str) else step.__name__),
                  reason,
                  file=sys.stderr)

        # Check for cycle:
        if step in predecessors:
            raise AssertionError(
                    "{}.{} -- cycle in step_fns: ({})"
                    .format(
                      context.url_class_name,
                      context.location,
                      ', '.join(fn.__name__
                                for fn
                                 in predecessors[predecessors.index(step):])))

        predecessors = predecessors + (step,)

        # Check max_milestone:
        if max_milestone is not None and not isinstance(step, str) and \
           step.milestone is not None and step.milestone > max_milestone:
            raise AssertionError(
                    "{}.{} -- milestone {!r} generated too soon, "
                    "predecessors: ({})"
                    .format(
                      context.url_class_name,
                      context.location,
                      step.__name__,
                      ', '.join(fn.__name__
                                for fn in predecessors)))

        # Generate prereqs:
        for prereq, prereq_reason in prereq_map[step]:
            yield from generate_step(prereq, context, prereq_map, seen,
                                     predecessors, max_milestone, trace,
                                     prereq_reason)

        if not isinstance(step, str):
            # Generate this step:
            if trace > 0:
                print("yielding", step.__name__, reason, file=sys.stderr)
            yield step
            seen.add(step)


if __name__ == "__main__":
    from . import step_utils
    for up in sorted(step_utils.get_unprovided_needs()):
        print(up)
