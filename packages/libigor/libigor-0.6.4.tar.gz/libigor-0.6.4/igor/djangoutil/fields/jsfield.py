# -*- coding: utf-8 -*-
import logging
import base64
import bz2
from six import with_metaclass, string_types
#from django.utils.timezone import now as _utcnow
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from igor.jsutil import jsobj, json_dumps, json_loads
try:
    from django.forms.utils import ValidationError
except ImportError:
    from django.forms.util import ValidationError


#==============================================================================
class JsFormField(forms.Field):
    """ Js form field """
    #------------------------------------------------------------------------//
    def to_python(self, value):
        if isinstance(value, string_types) or isinstance(value, (dict, jsobj)):
            try:
                return jsobj(value)
            except ValueError:
                import traceback; logging.error(traceback.format_exc())
                raise ValidationError(_("Enter valid JSON"))

        logging.info("RETURNING PLAIN VALUE")
        return value

    #------------------------------------------------------------------------//
    def clean(self, value):
        if not value and not self.required:
            return None

        if isinstance(value, dict):
            return jsobj(value)

        try:
            return super(JsFormField, self).clean(value)
        except TypeError:
            import traceback; logging.error(traceback.format_exc())
            raise ValidationError(_("Enter valid JSON"))


#==============================================================================
class JsField(with_metaclass(models.SubfieldBase, models.TextField)):
    #------------------------------------------------------------------------//
    def __init__(self, *args, **kw):
        super(JsField, self).__init__(*args, **kw)

    #------------------------------------------------------------------------//
    def to_python(self, value):
        if isinstance(value, (jsobj, list, dict)) or not value:
            return value

        try:
            return json_loads(value, jsobj)
        except:
            data    = base64.decodestring(value)
            val     = bz2.decompress(data)
            return json_loads(val, jsobj)

    #------------------------------------------------------------------------//
    def _serialize_item(self, value):
        try:
            return value.serialize()
        except AttributeError:
            return value

    #------------------------------------------------------------------------//
    def get_prep_value(self, value):
        return json_dumps(value)

    #------------------------------------------------------------------------//
    def formfield(self, **kw):
        kw.setdefault('form_class', JsFormField)
        return super(JsField, self).formfield(**kw)
