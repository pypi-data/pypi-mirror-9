# -*- coding: utf-8 -*-
import requests
from six import PY2, PY3
from igor.jsutil import json_loads, json_dumps, jsobj
if PY2:
    from urlparse import urljoin
elif PY3:
    from urllib.parse import urljoin


################
#  App runner  #
################


#----------------------------------------------------------------------------//
def run_app(App, cmdline):
    """
    :arg App: App class to execute
    :arg cmdline:   Global command line. The App class can define it's own
                    arguments, but here you can provide a global set of
                    arguments that superseeds the App defined set.

    An app should have the following interface:

    .. codeblock:: python

        class App():
            @classmethod
            def getcmdline(cmdline = None):
                '''Append arguments or return new cmdline if None is passed'''
                pass

            @classmethod
            def color_strings(color = True):
                '''Return strings for c(). Makes colors support much easier'''
                pass

            def __init__(args):
                '''Initialize app using cmdline arguments ``args``'''
                pass

            def execute():
                '''Execute app'''
                pass

    """

    cmdline = App.getcmdline(cmdline)
    args    = cmdline.parse_args()
    app     = App(args)
    app.execute()


#==============================================================================
class ColorPrinter(object):
    """  Colored string printing  """
    #------------------------------------------------------------------------//
    def __init__(self, colormap, usecolor = True):
        self.colormap = colormap
        self.usecolor = usecolor

    #------------------------------------------------------------------------//
    def printfn(self, string):
        print(string)

    #------------------------------------------------------------------------//
    def getstr(self, string):
        entry = self.colormap[string]
        if self.usecolor:
            return entry.c
        else:
            return entry.nc

    #------------------------------------------------------------------------//
    def get(self, msg, *args, **kw):
        msg = self.getstr(msg)
        if len(args) or len(kw):
            msg = msg.format(*args, **kw)
        return msg

    #------------------------------------------------------------------------//
    def cprint(self, msg, *args, **kw):
        msg = self.getstr(msg)
        if len(args) or len(kw):
            msg = msg.format(*args, **kw)

        self.printfn(msg)

    #------------------------------------------------------------------------//
    def __call__(self, msg, *args, **kw):
        """ Shortcut to cprint

        This allows the following construction
        >>> cprint = ColorPrinter({'msg': jsobj(c='c msg', nc='nc msg')})
        >>> cprint('msg')
        """
        return self.cprint(msg, *args, **kw)


#==============================================================================
class SimpleHttpClient(object):
    #------------------------------------------------------------------------//
    def __init__(self, host):
        self.host = host

    #------------------------------------------------------------------------//
    def _mkurl(self, relurl):
        return urljoin(self.host, relurl)

    #------------------------------------------------------------------------//
    def get(self, relurl, *args, **kw):
        return requests.get(self._mkurl(relurl), *args, **kw)

    #------------------------------------------------------------------------//
    def post(self, relurl, *args, **kw):
        return requests.post(self._mkurl(relurl), *args, **kw)

    #------------------------------------------------------------------------//
    def put(self, relurl, *args, **kw):
        return requests.put(self._mkurl(relurl), *args, **kw)

    #------------------------------------------------------------------------//
    def delete(self, relurl, *args, **kw):
        return requests.delete(self._mkurl(relurl), *args, **kw)


#==============================================================================
class ApiHttpError(RuntimeError):
    def __init__(self, resp):
        self.resp = resp
        msg = "HTTP {method} {reqpath} failed".format(
            method      = self.resp.request.method,
            reqpath     = self.resp.request.path_url,
        )
        super(ApiHttpError, self).__init__(msg)


#==============================================================================
class ApiClient(SimpleHttpClient):
    def __init__(self, host):
        super(ApiClient, self).__init__(host)

    #------------------------------------------------------------------------//
    def mkuri(self, modelname, uid):
        return '/restapi/{model}/{id}'.format(model = modelname, id = uid)

    #------------------------------------------------------------------------//
    def get(self, model, id, fields, cls = None):
        uri = self.mkuri(model, id)
        r = super(ApiClient, self).get(uri, params = {
            '_fields':   fields
        })
        return json_loads(r.text, cls or jsobj)

    #------------------------------------------------------------------------//
    def geturi(self, uri, fields, cls = None):
        r = super(ApiClient, self).get(uri, params = {
            '_fields':   fields
        })
        if r.status_code == 200:
            return json_loads(r.text, cls or jsobj)
        else:
            raise ApiHttpError(r)

    #------------------------------------------------------------------------//
    def call(self, what, objid, args):
        model, method = what.split('.', 1)
        uri  = self.mkuri(model, objid) + '/' + method
        data = None if args is None else json_dumps(args)
        r    = super(ApiClient, self).post(uri, data=data)
        if r.status_code == 200:
            apir = json_loads(r.text, jsobj)
            return apir.result
        else:
            raise ApiHttpError(r)
