#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import re
import copy
import sys
from webob import Request, Response
from igor.jsutil import JsObj
from six import string_types


#{{{ Util
g_jinja_env = None


#----------------------------------------------------------------------------//
def template_response(status, template, context={}):
    import jinja2
    global g_jinja_env
    if g_jinja_env is None:
        g_jinja_env = jinja2.Environment(
            autoescape  = True,
            loader      = jinja2.FileSystemLoader('./frontend/html')
        )

    return Response(
        g_jinja_env.get_template(template).render(context),
        status          = status,
        content_type    ='text/html'
    )


#----------------------------------------------------------------------------//
def json_response(status, body, headers={}, **kw):
    """ Shortcut for creating JSON responses """
    from igor.jsutil import json_dumps
    response = Response(
        json_dumps(body),
        status          = status,
        content_type    = 'application/json'
    )

    for name, value in headers.iteritems():
        response[name] = value

    return response


#----------------------------------------------------------------------------//
def _get_mod_obj(path):
    modname, attrname = path.rsplit('.', 1)
    __import__(modname)
    mod = sys.modules[modname]
    return getattr(mod, attrname)


#----------------------------------------------------------------------------//
def resolv_obj(cls):
    """ It will return an instance of the class referenced by the ``cls``
    argument. ``cls`` can be an class (instance of type) or a string with the
    class name. In the former case, the funciton will just instantiate the
    object, in the latter it will first resolve the class using
    ``get_mod_obj()`` and then instantiate it. The default (no-argument)
    constructor is used to create objects.

    >>> resolv_obj(int)
    >>> resolv_obj('module.Class')
    """
    # if its a string, treat it as an import path
    obj = cls
    if isinstance(cls, str) or isinstance(cls, unicode):
        obj = _get_mod_obj(cls)

    # If its a class instantiate it
    if isinstance(cls, type):
        obj = cls()

    return obj
#}}}


#{{{ URL
#----------------------------------------------------------------------------//
def regex_from_template(template):
    def var2regex(var):
        """
        <name:regex>  ->  (?P<name>regex)
        <name>        ->  (?P<name>[^/]+)
        <:regex>      ->  (regex)
        """
        tmp   = var.group(1).split(':', 1)
        name  = tmp[0]

        if len(tmp) == 2:
            regex = '?[^/]+' if tmp[1] == '?' else tmp[1]
        else:
            regex = '[^/]+'

        fmt = r'(?P<{name}>{regex})' if name else r'({regex})'

        if regex[0] == '?':
            fmt   = fmt + '?'
            regex = regex[1:]

        return fmt.format(name = name, regex = regex)

    regex = re.sub(r'<(.*?)>', var2regex, template.strip('/'))
    return re.compile('^' + regex + '$')


#----------------------------------------------------------------------------//
def url(template, handler, **vars):
    return JsObj.mkflat({
        'template': template,
        'regex':    regex_from_template(template),
        'handler':  handler,
        'vars':     vars,
    })
#}}}


#==============================================================================
class WsgiApp(object):
    #------------------------------------------------------------------------//
    def __init__(self, urls):
        """ urls - list of (template, handler) tuples """
        if urls and isinstance(urls[0], string_types):
            for u in urls[1:]:
                if isinstance(u.handler, string_types):
                    u.handler = urls[0] + '.' + u.handler
            self.urls = urls[1:]
        else:
            self.urls = urls

    #------------------------------------------------------------------------//
    def __call__(self, environ, start_response):
        req     = Request(environ)
        resp    = self.dispatch(req)
        return resp(environ, start_response)

    #------------------------------------------------------------------------//
    def dispatch(self, req):
        path = req.path_info.strip('/')
        for url in self.urls:
            match = url.regex.match(path)
            if match:
                args, kw = self._build_args(url, match)
                return self._call_handler(req, url, args, kw)

        return Response(
            'Page not found',
            content_type= 'text/html',
            status      = 404
        )

    #------------------------------------------------------------------------//
    def _call_handler(self, req, url, args, kw):
        handler = resolv_obj(url.handler)
        view    = getattr(handler, '__call__')
        try:
            resp  = view(req, *args, **kw)
        except Exception:
            resp = Response(
                '<pre style="background-color: #ddd">{0}</pre>'.format(
                    traceback.format_exc()
                ),
                content_type="text/html",
                status=500
            )
        return resp

    #------------------------------------------------------------------------//
    def _build_args(self, url, match):
        kw      = copy.copy(url.vars)
        reqargs = match.groupdict()
        reqargs = dict((k, v) for k, v in reqargs.iteritems() if k and v)
        isarg   = lambda x: (x is not None) and (x not in reqargs.itervalues())
        args    = [g for g in match.groups() if isarg(g)]
        kw      = copy.copy(url.vars)
        kw.update(reqargs)
        return args, kw


#----------------------------------------------------------------------------//
def make_server(host, port, urls):
    from wsgiref.simple_server import make_server
    return make_server(host, port, WsgiApp(urls))
