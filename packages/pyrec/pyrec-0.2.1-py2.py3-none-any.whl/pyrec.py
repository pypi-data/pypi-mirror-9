"""
    pyrec.Record -- a record datatype for Python
    Copyright: 2014 Kalle Tuure
    License: MIT
"""

__all__ = ['Record']

import copy
import collections

try:
    string_type = basestring # PY2
    range = xrange
except NameError:
    string_type = str # PY3


class Record(object):
    """Similar to ``namedtuple`` but with mutable attributes"""

    __slots__ = ()

    @staticmethod
    def _make_class(name, fields, **kwargs):
        if isinstance(fields, string_type):
            fields = [s.strip() for s in fields.replace(',',' ').split()]
        elif not isinstance(fields, collections.Sequence):
            raise Exception("Record fields must be defined as a string, list, or tuple.")
        if len(fields) == 0:
            raise Exception("Record field definition contained no items.")
        attrs = {'__slots__' : list(fields)}
        if 'fill' in kwargs:
            attrs['_fill'] = kwargs['fill']
        cls = type(name, (Record,), attrs)
        return cls

    def __new__(cls, *args, **kwargs):
        if cls is Record:
            return Record._make_class(*args, **kwargs)
        else:
            return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        d = len(args) - len(self.__slots__)
        if d > 0:
            raise Exception("Too many positional arguments")
        if d < 0 and hasattr(self, '_fill'):
            args = args + (self._fill,) * -d
        if args:
            for i, value in enumerate(args):
                setattr(self, self.__slots__[i], value)
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
        for field in self.__slots__:
            if not hasattr(self, field):
                raise Exception("Too few arguments to populate {} fields"\
                                .format(len(self.__slots__)))

    def __getitem__(self, key):
        if isinstance(key, int):
            return getattr(self, self.__slots__[key])
        elif isinstance(key, slice):
            return tuple(self[k] for k in self.__slots__[key])
        else:
            return getattr(self, key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            setattr(self, self.__slots__[key], value)
        else:
            setattr(self, key, value)

    def __delitem__(self, key):
        raise TypeError("'{}' object doesn't support item deletion"\
                        .format(self.__class__.__name__))

    def __delattr__(self, name):
        raise TypeError("'{}' object doesn't support attribute deletion"\
                        .format(self.__class__.__name__))

    def __iter__(self):
        for k in self.__slots__:
            yield self[k]

    def _items(self):
        for k in self.__slots__:
            yield (k, self[k])

    def _to_dict(self):
        return collections.OrderedDict(self._items())

    def _update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _copy(self):
        record = copy.copy(self)
        return record

    def _replace(self, **kwargs):
        record = self._copy()
        record._update(**kwargs)
        return record

    def __repr__(self):
        items = ', '.join(('{0}={1}'.format(k, v) for k, v in self._items()))
        return '<Record object {0}({1})>'.format(self.__class__.__name__, items)

    def __len__(self):
        return len(self.__slots__)

    def __eq__(self, other):
        if not isinstance(other, Record):
            return False
        return tuple(self._items()) == tuple(other._items())

    def __ne__(self, other):
        return not self == other

