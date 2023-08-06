# -*- coding: utf-8 -*-
import logging
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


#----------------------------------------------------------------------------//
def perm_create(app, model, codename, name):
    ct = ContentType.objects.get(app_label=app, model=model)
    return Permission.objects.get_or_create(
        codename      = codename,
        name          = name,
        content_type  = ct
    )


#----------------------------------------------------------------------------//
def perm_create_many(app, model, *perms):
    """
    :arg app:       App label
    :arg model:     Database model
    :arg perms:     All remaining arguments should be 2 item tuples consisting
    of perm codename and name (description).

    >>> perm_create_many(
    >>>     'auth', 'User',
    >>>     ('my_perm1', 'This is my first perm'),
    >>>     ('my_perm2', 'This is my second perm'),
    >>>     ('my_perm3', 'This is my thirrd perm'),
    >>> )
    """
    for perm in perms:
        perm_create(app, model, perm[0], perm[1])


#----------------------------------------------------------------------------//
def perm_delete(app, model, codename):
    """ Delete permission from the database. """
    try:
        ct      = ContentType.objects.get(app_label=app, model=model)
        perm    = Permission.objects.get(codename=codename, content_type=ct)
        perm.delete()
    except Permission.ObjectDoesNotExist:
        logging.error("Trying to delete non-existing permission {0}".format(
            '{0}.{1}.{2}'.format(app, model, codename)
        ))
    except Permission.MultipleObjectsReturned:
        logging.error("Multiple permissions exist {}".format(
            '{0}.{1}.{2}'.format(app, model, codename)
        ))
