# -*- coding: utf-8 -*-
from igor.jsutil import json_dumps
from igor.djangoutil.http import apiret


#==============================================================================
class ApiError(RuntimeError):
    """ Api error """
    #------------------------------------------------------------------------//
    def __init__(self, code = None, **kw):
        self.kw     = kw
        if code is not None:
            self.code = code

    #------------------------------------------------------------------------//
    def as_response(self):
        return apiret(self.code, **self.kw)

    #------------------------------------------------------------------------//
    def __str__(self):
        return "[{0}] {1}".format(self.code, json_dumps(self.kw, indent = 2))


class InvalidCall(ApiError):
    code    = 40001


class InvalidHttpMethod(ApiError):
    code    = 40002


class InvalidPostData(ApiError):
    code    = 40003


class InvalidArg(ApiError):
    code    = 40004


class AlreadyExists(ApiError):
    code    = 40005


class NotFound(ApiError):
    code = 404


class ObjectNotFound(ApiError):
    code = 40401


class ModelNotFound(ApiError):
    code = 40402


class MethodNotFound(ApiError):
    code = 40403


class EndpointNotFound(ApiError):
    code = 40404
