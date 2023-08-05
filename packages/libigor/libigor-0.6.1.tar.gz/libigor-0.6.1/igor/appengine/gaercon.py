#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# ./rcon.py unpack_all
# ./rcon.py unpack --jargs '{"tempid": 142123123}'
# ./rcon.py unpack --args tempid=12314124
# ./rcon.py reset_db
import yaml
import requests
import logging
from igor.jsutil import json_loads, json_dumps
from six import PY2, PY3
if PY2:
    from urlparse import urljoin
elif PY3:
    from urllib.parse import urljoin


#----------------------------------------------------------------------------//
def RconUrl(val):
    if val == 'remote':
        try:
            with open('app.yaml') as fp:
                cfg = yaml.load(fp.read())
                val = 'http://{}.appspot.com'.format(cfg['application'])
        except:
            import traceback; logging.error(traceback.format_exc())
            pass

    elif not (val.startswith('http://') or val.startswith('https://')):
        val = 'http://' + val

    return urljoin(val, '/tasks')


#----------------------------------------------------------------------------//
def parse_cmdline(cmdline = None):
    from argparse import ArgumentParser
    if cmdline is None:
        cmdline = ArgumentParser()

    cmdline.add_argument(
        'task_name',
        type=str, nargs="?",
        help='Name of the task to execute'
    )

    cmdline.add_argument(
        '-H', '--host',
        dest='url', type=RconUrl, default='localhost:8000',
        help='Host on which the API call should be executed'
    )
    cmdline.add_argument(
        '-a', '--args',
        dest='args', type=str, nargs='*',
        help='Task arguments as KEY=VALUE pairs'
    )
    cmdline.add_argument(
        '-j', '--jargs',
        dest='jargs', type=json_loads, required=False,
        help='JSON object representing the arguments'
    )
    cmdline.add_argument(
        '-f', '--jargs-file',
        dest='jargs_file', type=str, required=False,
        help='Path to a file containing RFC arguments in JSON format'
    )
    cmdline.add_argument(
        '-l', '--list',
        dest='listcmds', action="store_true", default=False,
        help='List all available commands'
    )

    return cmdline.parse_args()


#----------------------------------------------------------------------------//
def start_task(url, name, args):
    payload = json_dumps({
        "name":     name,
        "args":     args,
        'action':   'sched',
    })

    print("\033[32mPOST \033[94m{0} \033[90m{1}\033[39m".format(
        url, payload
    ))
    return requests.post(url, data = payload)


#----------------------------------------------------------------------------//
def get_task_args(cmdline):
    args = {}
    if cmdline.jargs:
        args.update(cmdline.jargs)
    elif cmdline.jargs_file:
        with open(cmdline.jargs_file) as fp:
            args.update(json_loads(fp.read()))
    elif cmdline.args:
        for name, value in (a.split('=', 1) for a in cmdline.args):
            args.setdefault(name, value)
    return args


#----------------------------------------------------------------------------//
def autoexec():
    cmdline = parse_cmdline()
    if cmdline.listcmds:
        r   = requests.get(cmdline.url, params={"_list": True})
        if r.status_code == 200:
            resp  = r.json()
            print('\n'.join(resp['tasks']))
        else:
            print("FAILED\n{0}".format(r.text))
    else:
        return start_task(
            cmdline.url, cmdline.task_name, get_task_args(cmdline)
        )


if __name__ == '__main__':
    autoexec()
