# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist
from igor.batching import rangeiter


#----------------------------------------------------------------------------//
def update_or_create(model, _values = {}, **kw):
    """
    :arg model:     Model class.
    :arg _values:   The values of fields. Those fields won't be included in
                    the query for existing instance.
    :arg kw:        Query filter. Combined with **_values** it provides new
                    field values.

    Update existing or create new model instance. All keyword arguments
    except **_values** and **model** will be used as filter in a query for
    existing instance. **_values** should contain fields that should be used
    only as a values for update and not in the filtering.

    With the following setup:
    >>> from django.db import models
    >>>
    >>> class MyModel(models.Model):
    ...     name    = models.CharField(max_length=50)
    ...     age     = models.IntegerField()
    >>>
    >>> MyModel.objects.create(name='m1', age=15)
    >>> MyModel.objects.create(name='m2', age=20)

    This will find or create an instance named 'test' and set its 'age' value
    to 20
    >>> update_or_create(MyModel, name = 'm1', _values={'age': 20})
    >>> m1 = MyModel.objects.get(name = 'm1')
    >>> m1.age
    20
    """
    try:
        obj = model.objects.get(**kw)
    except ObjectDoesNotExist:
        kw.update(_values)
        obj = model.objects.create(**kw)
        return obj, True

    for name, value in _values.items():
        if hasattr(obj, name):
            setattr(obj, name, value)


#----------------------------------------------------------------------------//
def first(model, **flt):
    """
    :arg model:     Model or query set.
    :return:        The first result of the queryset or the first result
                    returned by the query defined using **flt**.

    Get the first result of a query set, or query the db for first
    result given the filter.

    >>> from django.db import models
    >>>
    >>> class MyModel(models.Model):
    ...     name = models.CharField(max_length=50)
    ...     class Meta:
    ...         app_label = 'playground'
    >>>
    >>> a = first(MyModel, name='test')
    >>> b = first(MyModel.objects.filter(name = 'test'))
    >>> a == b
    True
    """
    if len(flt):
        try:
            return model.objects.get(**flt)
        except model.DoesNotExist:
            return None
        except model.MultipleObjectsReturned:
            return list(model.objects.filter(**flt)[0:1])[0]
    else:
        try:
            return model[0]
        except IndexError:
            return None


#----------------------------------------------------------------------------//
def drop(mode, models):
    def drop_slow(Model):
        logging.info("Slowly dropping all {}".format(Model.__name__))
        allitems = list(Model.objects.all())
        for o in allitems:
            o.delete()

    def drop_fast(Model):
        """ Might not call custom model delete method """
        total = Model.objects.all().count()
        logging.info("Dropping all {0} {1}".format(total, Model.__name__))
        Model.objects.all().delete()

    def drop_batch_fast(Model):
        """ Might not call custom model delete method """
        kBatchSize  = 100
        total       = Model.objects.all().count()
        logging.info("Dropping {0} {1}".format(total, Model.__name__))
        for beg, end in rangeiter(total, kBatchSize):
            logging.info("    -> {0}:{1}".format(beg, end))
            Model.objects.all()[beg:end].delete()

    def drop_batch_slow(Model):
        """ Might not call custom model delete method """
        kBatchSize  = 100
        total       = Model.objects.all().count()
        logging.info("Dropping {0} {1}".format(total, Model.__name__))
        for beg, end in rangeiter(total, kBatchSize):
            logging.info("    -> {0}:{1}".format(beg, end))
            objs = list(Model.objects.all()[beg:end])
            for o in objs:
                o.delete()

    dropfn = {
        'fast':         drop_fast,
        'slow':         drop_slow,
        'batch_fast':   drop_batch_fast,
        'batch_slow':   drop_batch_slow,
    }.get(mode, drop_batch_slow)

    for Model in models:
        dropfn(Model)
