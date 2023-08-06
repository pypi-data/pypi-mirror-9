# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json
from datetime import datetime as Datetime, date as Date
from decimal import Decimal as Dec
from pprint import pformat
from igor.traits import iterable
from six import string_types


kNameFilter = [
    lambda n: not(n.startswith('__') or n.endswith('__'))
]
parsers = [
    lambda x: Datetime.strptime(x, '%Y-%m-%d').date(),
    lambda x: Datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'),
    #lambda x: Datetime.strptime(x, '%Y-%m-%d'),
    #lambda x: parse_dt(x),
]
writers = [
    (
        lambda x: isinstance(x, Dec),
        lambda x: float(x)
    ),
    (
        lambda x: isinstance(x, (Date, Datetime)),
        lambda x: x.isoformat()
    ),
    (
        lambda x: hasattr(x, 'serialize') and callable(x.serialize),
        lambda x: x.serialize()
    ),
    (
        lambda x: iterable(x),
        lambda x: [write_value(i) for i in x]
    )
]


#----------------------------------------------------------------------------//
def dict2members(d):
    """ For every subdict create a jsobj from it, the same for list
    items, and return as a dictionary that corresponds to jsobj.members().
    It can be used to easily create a new dobj from it"""
    def mkval(val):
        if isinstance(val, string_types):
            pass
        elif isinstance(val, dict):
            val = jsobj(val)
        else:
            # check if it is an array
            try:
                val = [mkval(v) for v in val]
            except:
                pass
        return val

    return dict((n, mkval(v)) for n, v in d.items())


#----------------------------------------------------------------------------//
def parse_value(value):
    global parsers
    for parser in parsers:
        try:
            return parser(value)
        except:
            pass

    return value


#----------------------------------------------------------------------------//
def write_value(value):
    global writers
    try:
        for check, writer in writers:
            if check(value):
                return writer(value)
    except:
        pass
    return value


#----------------------------------------------------------------------------//
def json_dumps(obj, indent = 2):
    return json.dumps(obj, indent = indent, default = write_value)


#----------------------------------------------------------------------------//
def json_loads(jsonStr, cls=None):
    Class = cls or dict
    pairs_hook = lambda items: Class((n, parse_value(v)) for n, v in items)
    return json.loads(jsonStr, object_pairs_hook=pairs_hook)


#----------------------------------------------------------------------------//
def raw_json_loads(jsonStr):
    return json.loads(jsonStr)


#==============================================================================
class jsobj(dict):
    #------------------------------------------------------------------------//
    def __init__(self, *args, **kw):
        if len(args) == 1 and isinstance(args[0], string_types):
            for key, value in json_loads(args[0], jsobj).items():
                self[key] = value
        else:
            super(jsobj, self).__init__(*args, **kw)

    #------------------------------------------------------------------------//
    def members(self):
        return dict(self.items())

    #------------------------------------------------------------------------//
    def dumps(self, indent = 2):
        return json_dumps(self, indent)

    #------------------------------------------------------------------------//
    @classmethod
    def mkflat(self, d):
        ret = jsobj()
        for name, value in d.items():
            setattr(ret, name, value)
        return ret

    #------------------------------------------------------------------------//
    def __repr__(self):
        return '<{0}>'.format(str(self))

    #------------------------------------------------------------------------//
    def __str__(self, indent = None):
        """ Use JSON as string representation """
        return str(self.__unicode__(indent))

    #------------------------------------------------------------------------//
    def __unicode__(self, indent = None):
        return json_dumps(self, indent=indent)

    #------------------------------------------------------------------------//
    def __setattr__(self, name, value):
        self[name] = value

    #------------------------------------------------------------------------//
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError("No attribute {}".format(name))
