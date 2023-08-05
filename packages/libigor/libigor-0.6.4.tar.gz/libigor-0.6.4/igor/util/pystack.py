#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
from datetime import date as Date, datetime as Datetime
from igor.jsutil import jsobj
from igor.serialize import serialize_dict, serialize_object


#----------------------------------------------------------------------------//
def serialize_locals(vars):
    from igor.serialize import kPrimitives
    ret = {}

    def dumpval(name, val):
        if isinstance(val, (Date, Datetime)):
            return val.isoformat()
        return val

    # Filter callables
    vars = dict((n, v) for n, v in vars.items() if not callable(v))
    for name, value in vars.items():
        if isinstance(value, kPrimitives):
            ret[name] = dumpval(name, value)
        elif isinstance(value, dict):
            ret[name] = serialize_dict(value, '*', dumpval)
        elif isinstance(value, object):
            # Check if it's not a file object, or the iterable serializer will
            # iterate over it and we'll get a bad behaviour
            if not(hasattr(value, 'flush') and hasattr(value, 'readline')):
                ret[name] = serialize_object(value, '*', dumpval)
        else:
            ret[name] = repr(value)

    return ret


#----------------------------------------------------------------------------//
def process_frames(frames):
    dump  = []
    for frame, filename, lineno, func, src, srcidx in frames:
        dump.append(jsobj.mkflat({
            'filename':     filename,
            'lineno':       lineno,
            'func':         func,
            'srccontext':   src[0],
            'src':          inspect.getsourcelines(frame),
            'srcidx':       srcidx,
            'locals':       serialize_locals(frame.f_locals)
        }))
    return dump


#----------------------------------------------------------------------------//
def get_current_stack(context = 1):
    frame       = inspect.currentframe().f_back
    framelist   = []
    while frame:
        try:
            finfo = inspect.getframeinfo(frame, context)
        except:
            break

        framelist.append((frame,) + finfo)
        frame = frame.f_back
    return framelist


#----------------------------------------------------------------------------//
def dump_stack(include_caller = True):
    """
    :arg include_caller:    If set to ``False`` it won't include the function
                            calling ``dump_trace()`` withing
    """
    stack = get_current_stack()
    #stack = inspect.stack()
    stack = stack[1 if include_caller else 2:]
    stack.reverse()
    return process_frames(stack)


#----------------------------------------------------------------------------//
def dump_trace(include_caller = True):
    return process_frames(inspect.trace())


#----------------------------------------------------------------------------//
def print_dump(dump):
    for f in dump:
        print('\n')
        print('-' * 80)
        print("{0}:{1}:   {2}".format(f.filename, f.lineno, f.func))
        for line in f.src[0]:
            print('{0} {1}'.format(
                '>>>' if line == f.srccontext else '...',
                line.rstrip()
            ))

        print('\nLocals:')
        for name, value in f.locals.items():
            print('     {0:15}: {1}'.format(name, value))
