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
import re
import logging
from inspect import getdoc
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from google.appengine.api import taskqueue
#from igor.jsutil import jsobj, json_dumps
from igor.jsutil import json_dumps, jsobj
from igor.djangoutil.http import HttpResponse
from igor.serialize import serialize
from django.core.urlresolvers import reverse
from .util import get_args, parse_args, apiret, json_response


#==============================================================================
class TaskRunner(View):
    """ task runner
    TaskDesc:
        name
        module
        fnRun
    """
    _tasks = {}

    #------------------------------------------------------------------------//
    @classmethod
    def _find(self, name, group = None):
        return self._tasks.get(name)

    #------------------------------------------------------------------------//
    @classmethod
    def _add_function_task(self, fn, **extra):
        name             = fn.__name__
        fn._args, fn._kw = get_args(fn)
        return jsobj(
            name    = name,
            module  = fn.__module__.rsplit('.', 1)[1],
            runfn   = fn,
            args    = fn._args,
            kw      = fn._kw,
            **extra
        )

    #------------------------------------------------------------------------//
    @classmethod
    def _add_class_task(self, cls, **extra):
        s1      = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name    = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        fn      = cls()
        fn._args, fn._kw = get_args(fn.run)
        fn._args.remove('self')
        return jsobj(
            name    = name,
            module  = fn.__module__.rsplit('.', 1)[1],
            runfn   = fn.run,
            args    = fn._args,
            kw      = fn._kw,
            **extra
        )

    #------------------------------------------------------------------------//
    @classmethod
    def register(self, *args, **kw):
        """ Decorator for registering tasks (function or class). """
        if len(args) == 1 and len(kw) == 0:
            fn = args[0]
            if isinstance(fn, type):
                tdesc = self._add_class_task(fn, **kw)
            else:
                tdesc = self._add_function_task(fn, **kw)

            self._tasks[tdesc.name] = tdesc
            return fn
        else:
            def wrapper(fn):
                return fn
            return wrapper

    #------------------------------------------------------------------------//
    @classmethod
    def schedule(self, _name, _queue = None, _eta = None, **args):
        params  = {
            'url':      reverse('task-runner'),
            'payload':  json_dumps({'name': _name, 'args': args}),
            'eta':      _eta,
        }
        _queue is not None and params.setdefault('queue_name', _queue)
        logging.info("Scheduling {0}{2}: {1}".format(
            _name, json_dumps(args),
            ' at {}'.format(_eta.isoformat(' ')) if _eta is not None else ''
        ))
        #logging.info("Scheduling {0}: {1}".format(_name, json_dumps(args)))
        return taskqueue.add(**params)

    #------------------------------------------------------------------------//
    @classmethod
    def execute(self, req, name, args):
        logging.info("Executing {}".format(name))
        tdesc  = self._find(name)
        if tdesc is None:
            msg = "Task {} not found".format(name)
            logging.error(msg)
            return apiret(40401, msg = msg)

        a, kw = parse_args(args, tdesc.args, tdesc.kw)
        try:
            return tdesc.runfn(*a, **kw)
        except Exception as ex:
            #from stratego.models import Incident
            #Incident.trace()
            logging.error("Task execution {} failed".format(name))
            import traceback; logging.error(traceback.format_exc())
            return apiret(20000, msg='Task failed', exception=str(ex))

    #------------------------------------------------------------------------//
    @method_decorator(csrf_exempt)
    def dispatch(self, req, *args, **kw):
        if req.method == 'POST':
            body = jsobj(req.body)
            if 'action' not in body or body.action == 'exec':
                ret = self.execute(req, body.name, body.args)
                if isinstance(ret, HttpResponse):
                    return ret
                else:
                    return json_response(200, serialize(ret, '**'))
            else:
                self.schedule(body.name, **body.args.members())
                return apiret(
                    msg     = 'Task started',
                    url     = req.path_info,
                    args    = body.args.members(),
                )

        elif req.method == 'OPTIONS':
            tasks = sorted(self._tasks.values(), key=lambda x: x.name)
            return apiret(tasks = serialize(tasks, '*'))
        elif req.method == 'GET':
            if '_name' not in req.GET:
                if '_list' in req.GET:
                    return apiret(tasks = self._tasks.keys())
            else:
                taskName    = req.GET['_name']
                #taskfn      = self._tasks.get(taskName)
                tdesc      = self._find(taskName)
                if tdesc is None:
                    return apiret(
                        40401, msg="Task {} not found".format(taskName)
                    )

                if '_start' in req.GET:
                    qs = dict((n, v) for n, v in req.GET.iteritems())
                    qs.pop('_name')
                    qs.pop('_start')
                    self.schedule(req.GET['_name'], **qs)
                    return apiret(
                        msg = 'Task started',
                        url = req.path_info,
                        args = qs,
                    )
                else:
                    # Return documentation
                    return apiret(
                        name        = taskName,
                        args        = tdesc.args,
                        kwargs      = tdesc.kw,
                        description = getdoc(tdesc.runfn),
                    )

        return apiret(40001, msg="Cannot process call")
