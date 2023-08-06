# -*- coding: utf-8 -*-


#----------------------------------------------------------------------------//
def insert_sorted(items, value, key = lambda x: x):
    """ Insert into sorted collection and return the index of the new item """
    idx = 0
    kv  = key(value)
    idx = next((i for i, x in enumerate(items) if key(x) < kv), len(items))
    idx = idx if idx >= 0 else 0
    items.insert(idx, value)
    return idx


