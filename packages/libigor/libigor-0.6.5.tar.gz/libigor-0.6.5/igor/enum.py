# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from six import string_types, integer_types
from itertools import chain


#==============================================================================
class EnumMetaclass(type):
    """Metaclass for enumerations.
    You must define the values using UPPERCASE names.

    Generates:
    cls.names - reverse dictionary mapping value to name
    cls.pairs - sorted list of (id, name) pairs suitable for model choices
    cls.values - list of values defined by the enumeration
    cls.trans_name - reverse dictionary mapping value to string ready for
    translation

    Example:
    class X(object):
        __metaclass__ = EnumMetaclass
        A = 1
        B = 2
        C = 3

    >>> X.names
    {1: 'A', 2: 'B', 3: 'C'}

    >>> X.values
    [1, 2, 3]

    >>> X.pairs
    [(1, 'A'), (2, 'B'), (3, 'C')]

    >>> X.trans_names
    {1: 'X.A', 2: 'X.B', 3: 'X.C'}
    """
    allowedTypes = tuple(chain(string_types, integer_types, [float]))

    def __new__(cls, name, bases, attrs):
        names       = {}
        trans_names = {}
        str2val     = {}
        isval       = lambda x: x.isupper() or x[0].isupper()

        for attrname, attrval in attrs.items():
            #if attrname.isupper() and isinstance(attrval, cls.allowedTypes):
            if isval(attrname) and isinstance(attrval, cls.allowedTypes):
                str2val[attrname]    = attrval
                names[attrval]       = attrname
                trans_names[attrval] = name + u"." + attrname

        attrs['names']       = names
        attrs['choices']     = sorted(names.items())
        attrs['str2val']     = str2val
        attrs['values']      = sorted(names.keys())
        attrs['trans_names'] = trans_names

        return type.__new__(cls, name, bases, attrs)


#==============================================================================
class Enum(object):
    __metaclass__ = EnumMetaclass
