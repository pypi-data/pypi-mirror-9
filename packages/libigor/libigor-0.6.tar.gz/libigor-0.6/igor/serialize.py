"""
TODO:
    - [ ] Support list fields
    - [ ] Add href support
"""
import logging
from datetime import date as Date, datetime as Datetime
from decimal import Decimal
#from django.db.models import Model
from itertools import chain
from six import integer_types, string_types, binary_type
from igor.fieldspec import Fieldspec
from igor.traits import iterable
from igor.jsutil import jsobj
from igor.enum import Enum

kPrimitives = tuple(chain(
    integer_types,
    string_types,
    (float, binary_type, Date, Datetime, Decimal)
))


#==============================================================================
class Priority(Enum):
    """
    **HIGH**
        Serializers matching (almost) exactly, very strict. The client code
        should assume, that the serializer implements perfect or near perfect
        serialization for all of it's matching types.

    **MEDIUM**
        Serializer is able to do a decent job at serializing its input values.
        This priority should be used for a more general type matchers and as
        a "decent polyfill" - Means it can be improved, but it's working well
        for now.

    **LOW**
        This priority should be used by all serializers that match a wide
        range of types. In most cases this will be used as a fallback, i.e. no
        serializers with higher priority (better support for the type) match.
    """
    HIGH    = 100   # Serializers matching (almost) exactly, very strict. The
    MEDIUM  = 50
    LOW     = 0


#----------------------------------------------------------------------------//
def dumpval(name, value):
    if isinstance(value, (Date, Datetime)):
        return value.isoformat()
    return value


#==============================================================================
class Serializer(object):
    """
    HIGH priority is for serializers with a strict selector.
    >>> @serializer.add(Priority.HIGH, lambda o: isinstance(o, Model))
    ... def serialize_model(model, fieldspec, dumpval):
    ...     pass

    >>> @serializer.add(Priority.HIGH, lambda o: isinstance(o, dict))
    ... def serialize_dict(model, fieldspec, dumpval):
    ...     pass

    >>> @serializer.add(Priority.HIGH, lambda o: isinstance(o, jsobj))
    ... def serialize_jsobj(model, fieldspec, dumpval):
    ...     pass

    >>> @serializer.add(Priority.HIGH,
    ...     lambda o: isinstance(o, (int, float, str, unicode, bytes))
    ... )
    ... def serialize_primitive(model, fieldspec, dumpval):
    ...     pass

    MEDIUM priority since this will catch every iterable, and we might want
    a more custom serializer.
    >>> @serializer.add(Priority.MEDIUM, lambda o: iterable(o))
    ... def serialize_iterable(model, fieldspec, dumpval):
    ...     pass

    Low because it will catch almost everything. This is a kind of general
    fallback if we don't have specialized serializer.
    >>> @serializer.add(Priority.LOW, lambda o: isinstance(o, object))
    ... def serialize_object(model, fieldspec, dumpval):
    ...     pass
    """

    #------------------------------------------------------------------------//
    def __init__(self):
        self.serializers = {}

    #------------------------------------------------------------------------//
    def add(self, priority, check):
        def decorator(fn):
            """
            >>> ismodel = lambda o: isinstance(o, Model)
            >>> @serializer.add.add(Priority.HIGH, ismodel)
            ... def serialize_model(model, fieldspec, dumpval):
            ...     # ...
            """
            fn._serializer_priority  = priority
            fn._serializer_check     = check
            if priority not in self.serializers:
                self.serializers[priority] = [fn]
            else:
                self.serializers[priority].append(fn)
            return fn

        return decorator

    #------------------------------------------------------------------------//
    def serialize(self, obj, fieldspec = '*', dumpval = dumpval):
        serializer = self.find(obj)
        return serializer(obj, fieldspec, dumpval)

    #------------------------------------------------------------------------//
    def find(self, obj, minpriority = Priority.LOW):
        serializer = None
        for priority in sorted(self.serializers.keys(), key = lambda x: -x):
            if priority >= minpriority:
                for s in self.serializers[priority]:
                    if s._serializer_check(obj):
                        serializer = s
                        break
                else:
                    continue
                break
        else:
            raise ValueError("Don't know how to serialize {}".format(
                str(type(obj))
            ))
        return serializer


serializer = Serializer()


#----------------------------------------------------------------------------//
@serializer.add(Priority.HIGH, lambda o: isinstance(o, dict))
def serialize_dict(dct, fieldspec, dumpval = dumpval):
    """ Serialize dictionary. """
    ret         = {}

    if not isinstance(fieldspec, Fieldspec):
        fieldspec   = Fieldspec(fieldspec)

    if fieldspec.empty():
        return {}

    for name, value in dct.items():
        if name in fieldspec:
            try:
                fn = serializer.find(value, Priority.MEDIUM)
                if fn is not None:
                    ret[name]   = fn(value, fieldspec[name], dumpval)
                else:
                    ret[name] = dumpval(name, value)
            except ValueError:
                #import ipdb; ipdb.set_trace()
                #ret[name] = dumpval(name, value)
                #ret[name] = serialize_object(name, value)
                pass

    return ret


#----------------------------------------------------------------------------//
@serializer.add(Priority.HIGH, lambda o: isinstance(o, jsobj))
def serialize_jsobj(obj, fieldspec, dumpval):
    if not isinstance(fieldspec, Fieldspec):
        fieldspec   = Fieldspec(fieldspec)

    return serialize_dict(obj.serialize(), fieldspec, dumpval)


#----------------------------------------------------------------------------//
@serializer.add(Priority.HIGH, lambda o: isinstance(o, kPrimitives))
def serialize_primitive(obj, fieldspec, dumpval):
    if not isinstance(fieldspec, Fieldspec):
        fieldspec   = Fieldspec(fieldspec)

    return dumpval('', obj)


#----------------------------------------------------------------------------//
@serializer.add(Priority.MEDIUM, lambda o: iterable(o))
def serialize_iterable(obj, fieldspec, dumpval):
    if not isinstance(fieldspec, Fieldspec):
        fieldspec   = Fieldspec(fieldspec)

    ret = []
    for item in obj:
        ret.append(serializer.serialize(item, fieldspec))
    return ret
    #return [serializer.serialize(item) for item in obj]


#----------------------------------------------------------------------------//
def isfileobj(obj):
    return hasattr(obj, 'flush') and hasattr(obj, 'readline')


#----------------------------------------------------------------------------//
@serializer.add(Priority.LOW, lambda o: isinstance(o, object))
def serialize_object(obj, fieldspec = '*', dumpval = dumpval):
    if not isinstance(fieldspec, Fieldspec):
        fieldspec   = Fieldspec(fieldspec)

    if fieldspec.empty():
        return {}

    filters = [
        lambda n, v: not (n.startswith('__') or n.endswith('__')),
        lambda n, v: not callable(v),
        lambda n, v: not isfileobj(v),
    ]
    #filters = [
    #    lambda n: not(n.startswith('__') or n.endswith('__')),
    #    lambda n: not callable(getattr(obj, n)),
    #    lambda n: not isfileobj(getattr(obj, n)),
    #]

    def isval(name, value):
        try:
            return all(flt(name, value) for flt in filters)
        except:
            return False

    ret = {}
    for name in dir(obj):
        if name in fieldspec:
            value = getattr(obj, name)
            if isval(name, value):
                try:
                    fn = serializer.find(value, Priority.MEDIUM)
                    if fn is not None:
                        ret[name]   = fn(value, fieldspec[name], dumpval)
                    else:
                        ret[name] = dumpval(name, value)
                except ValueError:
                    pass
    return ret

    #for name, value in dct.items():
    #    if name in fieldspec:
    #        try:
    #            fn = serializer.find(value, Priority.MEDIUM)
    #            if fn is not None:
    #                ret[name]   = fn(value, fieldspec[name], dumpval)
    #            else:
    #                ret[name] = dumpval(name, value)
    #        except ValueError:
    #            #import ipdb; ipdb.set_trace()
    #            #ret[name] = dumpval(name, value)
    #            #ret[name] = serialize_object(name, value)
    #            pass

    #return ret


#----------------------------------------------------------------------------//
#@serializer.add(Priority.LOW, lambda o: isinstance(o, object))
#def serialize_object(obj, fieldspec = '*', dumpval = dumpval):
#    if not isinstance(fieldspec, Fieldspec):
#        fieldspec   = Fieldspec(fieldspec)
#
#    filters = [
#        lambda n: not(n.startswith('__') or n.endswith('__')),
#        lambda n: not callable(getattr(obj, n)),
#        lambda n: not isfileobj(getattr(obj, n)),
#    ]
#    def isval(name):
#        try:
#            return all(flt(name) for flt in filters)
#        except:
#            return False
#    #isval   = lambda n: all(f(n) for f in filters)
#    objdict = dict((n, getattr(obj, n)) for n in dir(obj) if isval(n))
#    return serialize_dict(objdict, fieldspec, dumpval)


#----------------------------------------------------------------------------//
def serialize(obj, fieldspec = '*', dumpval = dumpval):
    """

    **Examples**

    With the following data (same applies to django models and ``jsobj``):

    >>> model = {
    ...     'field1': 10,
    ...     'field2': {
    ...         'sub1': 1,
    ...         'sub2': 2,
    ...     },
    ...     'field3': 20,
    ... }

    Here are a few examples of what fields would be selected by each
    fieldspec (second argument for ``serialize``):

    >>> from restapi.serialize import serialize
    >>> serialize(model, '*') == {
    ...     'field1': 10,
    ...     'field2': {},
    ...     'field3': 20
    ... }
    True

    Serialize only selected fields.

    >>> serialize(model, 'field1,field3') == {
    ...     'field1': 10,
    ...     'field3': 20
    ... }
    True

    Specify what fields to expand on an object.

    >>> serialize(model, 'field1,field2(sub1)') == {
    ...     'field1': 10,
    ...     'field2': {
    ...         'sub1': 1
    ...     }
    ... }
    True

    Wildcards (``*``) expand all fields for that given object, *without*
    expanding nested objects.

    >>> serialize(model, 'field1,field2(*)') == {
    ...     'field1': 10,
    ...     'field2': {
    ...         'sub1': 1,
    ...         'sub2': 2
    ...     }
    ... }
    True

    Double wirldcard (``**``) will expand all fields recursively. This is the
    most heavy call.

    >>> serialize(model, '**') == {
    ...     'field1': 10,
    ...     'field2': {
    ...         'sub1': 1,
    ...         'sub2': 2
    ...     },
    ...     'field3': 20
    ... }
    True

    """
    if not isinstance(fieldspec, Fieldspec):
        fieldspec   = Fieldspec(fieldspec)
    return serializer.serialize(obj, fieldspec, dumpval)
