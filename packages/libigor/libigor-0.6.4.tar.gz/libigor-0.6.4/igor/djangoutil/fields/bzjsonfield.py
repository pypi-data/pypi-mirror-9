# -*- coding: utf-8 -*-
import bz2
import base64
from six import with_metaclass
from django.db import models
from igor.jsutil import jsobj, json_dumps, json_loads
from igor.djangoutil.fields.jsonfield import JsonFormField


#==============================================================================
class BzJsonField(with_metaclass(models.SubfieldBase, models.TextField)):
    #------------------------------------------------------------------------//
    def __init__(self, *args, **kw):
        super(BzJsonField, self).__init__(*args, **kw)

    #------------------------------------------------------------------------//
    def to_python(self, value):
        """ """
        if isinstance(value, (jsobj, list, dict)) or not value:
            return value
        return json_loads(bz2.decompress(base64.decodestring(value)))

    #------------------------------------------------------------------------//
    def get_prep_value(self, value):
        """ Get DB value """
        return base64.encodestring(bz2.compress(json_dumps(value)))

    #------------------------------------------------------------------------//
    def formfield(self, **kw):
        kw.setdefault('form_class', JsonFormField)
        return super(BzJsonField, self).formfield(**kw)
