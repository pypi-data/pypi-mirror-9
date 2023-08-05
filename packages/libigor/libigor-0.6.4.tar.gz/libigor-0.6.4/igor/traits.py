#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import types
from inspect import ismethod
from six import string_types


#----------------------------------------------------------------------------//
def iterable(collection):
    """Checks if the variable is not a basestring instance and can be
    enumerated.
    """
    try:
        # strings can be iterated - that's not what we want
        if isinstance(collection, string_types):
            return False
        # avoid opening a generator
        if isinstance(collection, types.GeneratorType):
            return True
        for a in collection:
            break
        return True
    except (TypeError, AttributeError, KeyError):
        return False


#----------------------------------------------------------------------------//
def isstaticmethod(cls, name):
    method = getattr(cls, name)
    if ismethod(method) and method.__self__ is cls:
        return True
    return False


#----------------------------------------------------------------------------//
def methodtype(cls, name):
    """
    :return:    0 - Not a method
                1 - instance method
                2 - class method
    """
    method = getattr(cls, name)
    if ismethod(method):
        if method.__self__ is cls:
            return 2
        return 1
    return 0

