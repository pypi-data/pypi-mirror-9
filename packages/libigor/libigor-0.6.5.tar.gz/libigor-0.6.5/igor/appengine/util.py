"""
POST call:
JSON{
    name:       STR,
    args:       DICT
    action:     "sched | exec"
}

GET call:
    ?_name=STR&arg1=VAL&arg2=VAL

"""
import logging
import yaml
from six import PY2, PY3
from inspect import getargspec
from igor.jsutil import json_dumps
if PY2:
    from urlparse import urljoin
elif PY3:
    from urllib.parse import urljoin


#----------------------------------------------------------------------------//
def json_response(status, body, headers={}, **kw):
    """ Shortcut for creating JSON responses """
    from django.http import HttpResponse
    response = HttpResponse(
        json_dumps(body),
        status          = status,
        content_type    = 'application/json'
    )

    for name, value in headers.iteritems():
        response[name] = value

    return response


#----------------------------------------------------------------------------//
def apiret(code=20000, **kw):
    from django.conf import settings
    assert(code > 100)
    apiCodes = getattr(settings, 'API_CODES', {})
    kw.update({
        '_code':    code % 100,
        '_status':  apiCodes.get(code, 'Unknown'),
    })
    return json_response(code / 100, kw)


#----------------------------------------------------------------------------//
def get_args(fn):
    spec    = getargspec(fn)
    defLen  = len(spec.defaults) if spec.defaults is not None else 0
    lastArg = len(spec.args) - defLen
    args    = spec.args[:lastArg]
    kw      = dict(zip(spec.args[lastArg:], spec.defaults)) if defLen else {}
    return args, kw


#----------------------------------------------------------------------------//
def parse_args(args, argspec, kwspec):
    a, kw   = [], {}
    for arg in argspec:
        if arg not in args:
            raise ValueError('{} is required'.format(arg))
        a.append(args[arg])

    for name, value in kwspec.items():
        if name in args:
            kw[name] = args[name]

    return a, kw



#==============================================================================
class AppUrl(object):
    #------------------------------------------------------------------------//
    def __init__(self, relurl = '/'):
        self.relurl = relurl

    #------------------------------------------------------------------------//
    def __call__(self, val):
        if val == 'remote':
            try:
                with open('app.yaml') as fp:
                    cfg = yaml.load(fp.read())
                    val = 'http://{}.appspot.com'.format(cfg['application'])
            except:
                import traceback; logging.error(traceback.format_exc())
                pass

        elif not (val.startswith('http://') or val.startswith('https://')):
            val = 'http://' + val

        return urljoin(val, self.relurl)

AppHost = AppUrl('')

#----------------------------------------------------------------------------//
#def AppHost(val):
#    if val == 'remote':
#        try:
#            with open('app.yaml') as fp:
#                cfg = yaml.load(fp.read())
#                val = 'http://{}.appspot.com'.format(cfg['application'])
#        except:
#            import traceback; logging.error(traceback.format_exc())
#            pass
#
#    elif not (val.startswith('http://') or val.startswith('https://')):
#        val = 'http://' + val
#
#    return val


