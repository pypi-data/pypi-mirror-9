# -*- coding: utf-8 -*-
import logging
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
class JsonFormField(forms.Field):
    """ Js form field """
    #------------------------------------------------------------------------//
    def to_python(self, value):
        if isinstance(value, string_types):
            try:
                return json_loads(value)
            except ValueError:
                import traceback; logging.error(traceback.format_exc())
                raise ValidationError(_("Enter valid JSON"))

        logging.info("RETURNING PLAIN VALUE")
        return value

    #------------------------------------------------------------------------//
    def clean(self, value):
        if not value and not self.required:
            return None

        try:
            return super(JsonFormField, self).clean(value)
        except TypeError:
            import traceback; logging.error(traceback.format_exc())
            raise ValidationError(_("Enter valid JSON"))


#==============================================================================
class JsonField(with_metaclass(models.SubfieldBase, models.TextField)):
    #------------------------------------------------------------------------//
    def __init__(self, *args, **kw):
        super(JsonField, self).__init__(*args, **kw)

    #------------------------------------------------------------------------//
    def to_python(self, value):
        if isinstance(value, (jsobj, list, dict)):
            return value
        elif not value:
            return {}
        return json_loads(value)

    #------------------------------------------------------------------------//
    def get_prep_value(self, value):
        return json_dumps(value)
        #try:
        #    return json_dumps([json_dumps(v) for v in value])
        #except (ValueError, TypeError):
        #    return json_dumps(value)

    #------------------------------------------------------------------------//
    def formfield(self, **kw):
        kw.setdefault('form_class', JsonFormField)
        return super(JsonField, self).formfield(**kw)
