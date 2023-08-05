#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
USAGE:

from igor.util.fngroup import fngroup
cmd = FnGroup()


@cmd()
def first_cmd():
    pass

@cmd()
def second_cmd():
    pass

fcmd = cmd.get('first_cmd')
scmd = cmd.get('first_cmd')
fcmd_meta = cmd.getmeta('first_cmd')

"""
from igor.jsutil import jsobj


class InvalidIndex(ValueError):
    pass


#==============================================================================
class FnGroup(object):
    #------------------------------------------------------------------------//
    def __init__(self):
        self.fnmap = {}

    #------------------------------------------------------------------------//
    def _mkmeta(self, fn, args, kw):
        fnmeta = jsobj(
            name = fn.__name__,
            fn   = fn,
            args = args,
        )
        fnmeta.update(kw)
        return fnmeta

    #------------------------------------------------------------------------//
    def __call__(self, *args, **kw):
        def wrapper(fn):
            self.fnmap[fn.__name__] = self._mkmeta(fn, args, kw)
            return fn

        if len(kw) == 0 and len(args) == 1 and callable(args[0]):
            args = list(args)
            fn   = args.pop(0)
            args = tuple(args)
            return wrapper(fn)
        else:
            return wrapper

    #------------------------------------------------------------------------//
    def get(self, name):
        fnmeta = self.fnmap.get(name)
        if fnmeta is not None:
            return fnmeta.fn
        else:
            return None

    #------------------------------------------------------------------------//
    def get_meta(self, name):
        return self.fnmap.get(name)

    #------------------------------------------------------------------------//
    def all(self):
        return self.fnmap.values()


#==============================================================================
class IndexedFnGroup(FnGroup):
    def __init__(self, *indexes):
        super(IndexedFnGroup, self).__init__()
        self.indexes = indexes
        self.index   = dict((idx, {}) for idx in indexes)

    #------------------------------------------------------------------------//
    def _mkmeta(self, fn, args, kw):
        fnmeta = super(IndexedFnGroup, self)._mkmeta(fn, args, kw)
        for attr in self.indexes:
            if attr in kw:
                self.index[attr][kw[attr]] = fnmeta

        return fnmeta

    #------------------------------------------------------------------------//
    def get_by_index(self, index, value):
        try:
            meta = self.get_meta_by_index(index, value)
            if meta is None:
                return None
            return meta.fn
        except InvalidIndex:
            return None

    #------------------------------------------------------------------------//
    def find(self, index, value):
        if index not in self.indexes:
            raise InvalidIndex("The given index does not exist")

        return self.index[index].get(value)

