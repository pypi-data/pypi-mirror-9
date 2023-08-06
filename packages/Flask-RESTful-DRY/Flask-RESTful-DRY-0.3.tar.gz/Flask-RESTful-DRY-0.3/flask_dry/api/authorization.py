# authorization.py

from flask.ext.login import current_user, login_fresh

from .class_init import attrs


__all__ = ('Requirement', 'Signed_in', 'Not_signed_in', 'Anybody',
           'Base_auth_context', 'sort',
          )


class Requirement:
    r'''These represent an authorization requirement.

    These objects are stored in the api classes.

    These are intended to be immutable.

    The constructor allows you to place any additional attributes on the
    requirement for other uses.  By convention, attribute names starting with
    '_' do not affect how the Requirement validates against an authorization
    context.  One of these is the '_overrides' attribute, which should be a
    :class:`.class_init.attrs` that will be added to the url method execution
    context.

    The `validate` method returns True if valid, False is not valid with no
    reason given, and a str if not valid for that reason.

    Subclasses must define a validate(self, context, debug) method that return
    True if the requirement is met, and either False, or `reason` if not met.
    The `reason` is a str specifying what the user can do to meet this
    requirement.
    '''
    _overrides = attrs()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            #if key != '_overrides':
            #    print("{}.__init__ got key".format(self.__class__.__name__),
            #          key)
            setattr(self, key, value)
        self._keys = tuple(sorted(k for k in kwargs.keys() if k[0] != '_'))

    def equivalent(self, other):
        r'''Returns True if self validates identically to other.
        '''
        return self.__class__ == other.__class__ and \
               self._keys == other._keys and \
               all(getattr(self, k) == getattr(other, k) for k in self._keys)


class Signed_in(Requirement):
    level = 800
    must_be_fresh = False
    def __repr__(self):
        if self.must_be_fresh:
            return "<Signed_in: must_be_fresh>"
        return "<Signed_in>"

    def validate(self, context, debug):
        if current_user.is_authenticated() and (
               not self.must_be_fresh or login_fresh()):
            return True
        return False


class Not_signed_in(Requirement):
    level = 800
    def __repr__(self):
        return "<Not_signed_in>"

    def validate(self, context, debug):
        if not current_user.is_authenticated():
            return True
        return False


class Anybody(Requirement):
    level = 900
    def __repr__(self):
        return "<Anybody>"

    def validate(self, context, debug):
        return True


class Base_auth_context:
    r'''This caches validation results from the requirements.

    It does this because the link processing hits the same auth_context for
    every link that might be relevant to the current situation.
    '''
    def __init__(self):
        self.cache = {}

    def meets(self, requirement, debug):
        ans = self.cache.get(requirement, None)
        if ans is None:
            ans = self.cache[requirement] = requirement.validate(self, debug)
        return ans


def sort(*requirements):
    r'''Returns tuple of requirements sorted by increasing level.
    '''
    return tuple(sorted(requirements, key=lambda r: r.level))

