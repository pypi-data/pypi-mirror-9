#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# ./rcon.py unpack_all
# ./rcon.py unpack --jargs '{"tempid": 142123123}'
# ./rcon.py unpack --args tempid=12314124
# ./rcon.py reset_db
import requests
from igor.jsutil import json_loads, json_dumps
from .util import AppUrl


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
        dest='url', type=AppUrl('/tasks'), default='localhost:8000',
        help='Host on which the API call should be executed'
    )
    cmdline.add_argument(
        '-e', '--exec',
        dest='execute', action='store_true',
        help=('Execute the task instead of scheduling it. This way the task '
              'can return a value. Useful if the main task schedules more '
              'subtask but can return some kind of ID to keep track of the '
              'whole process. WARNING: This will be a regular HTTP call, so '
              'AppEngine request quotas apply, not the taskqueue ones.')
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

    print("\033[32mSCHEDULE \033[94m{0} \033[90m{1}\033[39m".format(
        url, payload
    ))
    return requests.post(url, data = payload)


#----------------------------------------------------------------------------//
def exec_task(url, name, args):
    payload = json_dumps({
        "name":     name,
        "args":     args,
        'action':   'exec',
    })

    print("\033[32mEXECUTE \033[94m{0} \033[90m{1}\033[39m".format(
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
