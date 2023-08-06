# -*- coding: utf-8 -*-


#----------------------------------------------------------------------------//
def revdictiter(dct):
    """ Iterate over reverse of the dct ({key: value} -> {value: key}) """
    for key, value in dct.items():
        yield value, key


#----------------------------------------------------------------------------//
def revdict(dct):
    """ Return reversed dct ({key: value} -> {value: key}) """
    return dict(revdictiter(dct))
