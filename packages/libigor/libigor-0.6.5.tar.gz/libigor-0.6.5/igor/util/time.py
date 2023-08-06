#!/usr/bin/env python
# -*- coding: utf-8 -*-
from six import string_types
from datetime import datetime as Datetime, timedelta as Timedelta
try:
    from dateutil.parser import parse as parse_dt
except ImportError:
    parse_dt = None


#----------------------------------------------------------------------------//
def parse_iso(s, sep = 'T'):
    fmt = '%Y:%m:%d' + sep + '%H:%M:%S'
    return Datetime.strptime(fmt, s)


#----------------------------------------------------------------------------//
def parse_tstamp(s):
    import dateutil.parser
    if isinstance(s, Datetime):
        return s
    return dateutil.parser.parse(s)


#----------------------------------------------------------------------------//
def fmtdelta(dt):
    if isinstance(dt, Timedelta):
        seconds = int(dt.total_seconds())
    else:
        seconds = dt

    ret     = []
    hours   = 0
    minutes = 0
    if seconds >= 3600:
        hours    = seconds / 3600
        seconds -= hours * 3600
        ret.append(str(hours) + 'h')

    if seconds >= 60:
        minutes  = seconds / 60
        seconds -= minutes * 60
        ret.append(str(minutes) + 'm')

    if seconds > 0:
        ret.append(str(seconds % 60) + 's')

    return ' '.join(ret)


#----------------------------------------------------------------------------//
def parse_delta(interval):
    """ [length][unit- m/h/s] """
    val   = int(interval[:-1])
    unit  = interval[-1].lower()
    if unit == 'h':
        return Timedelta(hours = val)
    elif unit == 'm':
        return Timedelta(minutes = val)
    elif unit == 's':
        return Timedelta(seconds = val)
    raise ValueError('Invalid interval unit')


#----------------------------------------------------------------------------//
def ensure_aware_datetime(val):
    import pytz
    if isinstance(val, string_types):
        val = parse_dt(val)

    if val.tzinfo is None:
        val = pytz.utc.localize(val)

    return val
