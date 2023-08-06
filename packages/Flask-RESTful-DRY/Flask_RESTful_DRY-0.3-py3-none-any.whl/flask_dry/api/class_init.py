# class_init.py

r'''This defines a metaclass that sets up the initial empty class namespace as
derived from the base classes, so that base class variables may be referenced
by the class body that populates the class.

Use :class:`.declarative` as the metaclass for your class to make this work.

Use :class:`.modifier` values in derived classes to modify the inherited values,
rather than replace them.

Use :class:`.attrs` as a bucket of attributes in the base class to allow
individual attribute overrides in derived classes without changing the attrs
in the base class.
'''

import sys
from copy import deepcopy


__all__ = ('declarative', 'attrs', 'modifier', 'extend', 'remove', 'lookup')


debug=False
def set_debug(d):
    global debug
    debug = d


class declarative(type):
    r'''Metaclass to provide the inherited attributes to the class body.

    The class body is the code indented under the class declaration.

        >>> class top(metaclass=declarative):
        ...     x = 1
        ...     y = attrs(a=5, b=6, c=(1,2,3))
        >>> class bottom(top):
        ...     x = x + 1
        ...     y.b = 22
        ...     y.c = extend(4,5,6)
        >>> bottom.x
        2
        >>> top.x
        1
        >>> bottom.y
        attrs(a=5, b=22, c=(1, 2, 3, 4, 5, 6))
        >>> top.y
        attrs(a=5, b=6, c=(1, 2, 3))
    '''
    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return inheriting_dict(bases)

    def __new__(cls, name, bases, namespace, **kwds):
        return super().__new__(cls, name, bases, dict(namespace))


class inheriting_dict(dict):
    r'''Used as a temporary namespace for class initialization.

    Copies values from the base classes as they are referenced in the class
    body.

    Used by :class:`.declarative`.

        >>> class a:
        ...     i = {'x': 1}
        ...     t = (1,2,3)
        >>> d = inheriting_dict([a])
        >>> d.get('i')
        {'x': 1}
        >>> d['i']
        {'x': 1}
        >>> d['i']['y'] = 12
        >>> sorted(d['i'].items())
        [('x', 1), ('y', 12)]
        >>> a.i
        {'x': 1}
        >>> d['t'] = extend(4,5,6)
        >>> d['t']
        (1, 2, 3, 4, 5, 6)
        >>> a.t
        (1, 2, 3)
    '''
    def __init__(self, bases):
        if debug: print("inherited_dict.__init__", bases, file=sys.stderr)
        if not bases:
            self._base = None
        elif len(bases) == 1:
            self._base = bases[0]
        else:
            self._base = type('bogus', bases, {})

    def __getitem__(self, key):
        if debug: print("inherited_dict.__getitem__", key, file=sys.stderr)
        try:
            return super().__getitem__(key)
        except KeyError:
            if debug:
                print("inherited_dict.__getitem__ got KeyError",
                      file=sys.stderr)
            if self._base is None:
                raise
            try:
                old_value = getattr(self._base, key)
            except AttributeError:
                if debug: print("inherited_dict.__getitem__ got AttributeError",
                      file=sys.stderr)
                raise KeyError(key)
            new_value = deepcopy(old_value)
            super().__setitem__(key, new_value)
            return new_value

    def get(self, key, default=None):
        if debug: print("inherited_dict.get", key, file=sys.stderr)
        try:
            return super().__getitem__(key)
        except KeyError:
            if debug: print("inherited_dict.get got KeyError", file=sys.stderr)
            if self._base is None:
                return default
            try:
                old_value = getattr(self._base, key)
            except AttributeError:
                if debug: print("inherited_dict.__getitem__ got AttributeError",
                      file=sys.stderr)
                return default
            new_value = deepcopy(old_value)
            super().__setitem__(key, new_value)
            return new_value

    def __setitem__(self, key, value):
        r'''Need this to be able to assign a :class:`.modifier` to values.
        '''
        if debug:
            print("inherited_dict.__setitem__", key, value, file=sys.stderr)
        if isinstance(value, modifier):
            if debug:
                print("inherited_dict.__setitem__", key, "modifying",
                      file=sys.stderr)
            super().__setitem__(key, value.update_value(self.get(key), self))
        else:
            super().__setitem__(key, value)
        if debug:
            print("inherited_dict.__setitem__", key, "done", file=sys.stderr)


class attrs:
    r'''Tracks which attributes have been set in _names.

    _names is a set.

        >>> a = attrs(x=1,y=2,z=3)
        >>> sorted(a._names)
        ['x', 'y', 'z']
        >>> a.x
        1
        >>> a.w = 44
        >>> a.w
        44
        >>> sorted(a._names)
        ['w', 'x', 'y', 'z']

    Provides a :method:`.copy` method to make a deep copy of the attrs
    object (calling copy on all attrs values).

        >>> bottom = attrs(z='bottom')
        >>> middle = attrs(b=bottom, y='middle')
        >>> top = attrs(m=middle, x='top')
        >>> top.m.b.z
        'bottom'
        >>> c = deepcopy(top)
        >>> c.m.b.z = 'c'
        >>> c.m.b.z
        'c'
        >>> top.m.b.z
        'bottom'

    Also provides a :method:`.copy_into` to copy its attributes into another
    object.  This does not copy any attribute names starting with '_'.

        >>> class other: pass
        >>> b = other()
        >>> b.x = 'b'
        >>> b._hidden = 'b'
        >>> top._hidden = 'top'
        >>> top.copy_into(b)
        >>> b.m.b.z
        'bottom'
        >>> b.x
        'top'
        >>> b._hidden
        'b'
        >>> b.m.b.z = 'b'
        >>> b.m.b.z
        'b'
        >>> top.m.b.z
        'bottom'
    '''
    def __init__(self, **attrs):
        for key, value in attrs.items():
            super().__setattr__(key, deepcopy(value))
        self._names = set(attrs.keys())

    def __repr__(self):
        return "attrs({})".format(
                             ', '.join("{}={!r}".format(name,
                                                        getattr(self, name))
                                       for name in sorted(self._names)))

    def __setattr__(self, key, value):
        if key[0] != '_':
            self._names.add(key)
        if isinstance(value, modifier):
            current_value = getattr(self, key, None)
            if current_value is None:
                super().__setattr__(key, deepcopy(value))
            elif isinstance(current_value, modifier):
                super().__setattr__(key, value.update_modifier(current_value))
            else:
                super().__setattr__(key, value.update_value(current_value,
                                                            self))
        else:
            super().__setattr__(key, deepcopy(value))

    def copy_into(self, obj):
        for name in self._names:
            value = deepcopy(getattr(self, name))
            if isinstance(value, modifier):
                setattr(obj, name,
                        value.update_value(getattr(obj, name, None), obj))
            else:
                setattr(obj, name, value)


class modifier:
    r'''Base class for all modifiers.

    Subclass must define update_modifier(orig_modifier) and update_value(obj,
    parent) methods.

    The update_modifier method is called to merge self into an existing
    modifier that is already stored on the target object.  It should check the
    type of it's argument (it could be anything).

    The update_value method is called to modify a non-modifier value that is
    already stored on the object.
    '''
    pass


class extend(modifier):
    r'''Used by :class:`.attrs` to extend a value, rather than replacing it.

    Also changes the constructor to take multiple arguments, rather than a
    single argument.

        >>> extend(1,2,3)
        extend(1, 2, 3)
        >>> class other: pass
        >>> b = other()
        >>> b.t = (1,2,3)
        >>> a = attrs(t=extend(4,5,6))
        >>> a.copy_into(b)
        >>> b.t
        (1, 2, 3, 4, 5, 6)
    '''
    def __init__(self, *values):
        self.values = values

    def __repr__(self):
        return "extend({})".format(', '.join(repr(x) for x in self.values))

    def update_modifier(self, orig):
        if not isinstance(orig, extend):
            raise ValueError(
                    "Can't combine an 'extend' object with a '{}' object"
                      .format(orig.__class__.__name__))
        return extend(*(self.values + orig.values))

    def update_value(self, obj, parent):
        if not isinstance(obj, tuple):
            raise ValueError("Can only extend a tuple, not a '{}' object"
                               .format(obj.__class__.__name__))
        return obj + self.values


class remove(modifier):
    r'''Used by :class:`.attrs` to remove items from a tuple.

        >>> remove(1,2,3)
        remove(1, 2, 3)
        >>> class other: pass
        >>> b = other()
        >>> b.t = (1,2,3)
        >>> a = attrs(t=remove(1,3))
        >>> a.copy_into(b)
        >>> b.t
        (2,)
    '''
    def __init__(self, *values):
        self.values = values

    def __repr__(self):
        return "remove({})".format(', '.join(repr(x) for x in self.values))

    def update_modifier(self, orig):
        if not isinstance(orig, remove):
            raise ValueError(
                    "Can't combine a 'remove' object with a '{}' object"
                      .format(orig.__class__.__name__))
        return remove(*(self.values + orig.values))

    def update_value(self, obj, parent):
        if isinstance(obj, str) or not hasattr(obj, '__iter__'):
            raise ValueError("Can only remove from a sequence, not a '{}' "
                             "object"
                               .format(obj.__class__.__name__))
        return tuple(x for x in obj if x not in self.values)


class lookup(modifier):
    r'''Looks up a dotted reference in the object that it's copied into.

        >>> lookup('a.b')
        lookup('a.b')
        >>> class other: pass
        >>> b = other()
        >>> b.t = (1,2,3)
        >>> b.a = other()
        >>> b.a.b = 'hi mom'
        >>> a = attrs(t=lookup('a.b'))
        >>> a.copy_into(b)
        >>> b.t
        'hi mom'
    '''
    def __init__(self, reference):
        self.references = tuple(reference.split('.'))

    def __repr__(self):
        return "lookup('{}')".format('.'.join(self.references))

    def update_modifier(self, orig):
        r'''Overrides any other value or modifier.
        '''
        return self

    def update_value(self, obj, parent):
        ans = parent
        for attr in self.references:
            ans = getattr(ans, attr)
        return ans
