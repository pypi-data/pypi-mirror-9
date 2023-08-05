# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse
from igor.jsutil import json_dumps


#----------------------------------------------------------------------------//
def json_response(status, body, headers={}, **kw):
    """ Create JSON response. """
    response = HttpResponse(
        content         = json_dumps(body),
        status          = status,
        content_type    = 'application/json'
    )

    for name, value in headers.items():
        response[name] = value

    return response


#----------------------------------------------------------------------------//
def apiret(code=200, **kw):
    """ Return standard API response. """
    if 100 < code < 1000:
        # HTTP code
        code = code * 100
    elif code < 100:
        raise ValueError("Invalid return code")

    apiCodes = getattr(settings, 'API_CODES', {})
    kw.update({
        '_code':    code % 100,
        '_status':  apiCodes.get(code, 'Unknown'),
    })
    return json_response(int(code / 100), kw)


#----------------------------------------------------------------------------//
def invalid_arg(cond, msg):
    """ Return invalid argument response if *cond* evaluates to ``True``. """
    from gaetasks.views import apiret
    if cond:
        return apiret(40101, msg=msg)
