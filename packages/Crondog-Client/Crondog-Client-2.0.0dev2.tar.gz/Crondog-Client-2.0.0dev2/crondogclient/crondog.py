#!/usr/bin/env python
from __future__ import print_function

__VERSION__="2.0.0dev2"

RETURN_CODE_SUCCESS=0
RETURN_CODE_ERROR_NO_CMD=1002

import os
import argparse
from .core import send_data, run_command, handle_normally


API_ENDPOINT = 'http://crondog.hauntdigital.co.nz/api/v1/job'

def main():
    parser = argparse.ArgumentParser(description="A cron job wrapper that sends cron output to cronscape Version %s" % __VERSION__)
    parser.add_argument('-k', '--key', help='Cronscape API key.')
    parser.add_argument('-c', '--cmd', help='Run a command. Could be `cronscape -c "ls -la"`.')

    namespace, sys_args = parser.parse_known_args()

    key=namespace.key if namespace.key else os.environ['CRONDOG_API_KEY'] if 'CRONDOG_API_KEY' in os.environ else None
    cmd=namespace.cmd if namespace.cmd else None

    if not cmd:
        print('\n\n\tA command must be specified\n\n')
        parser.print_help()
        exit(RETURN_CODE_ERROR_NO_CMD)

    command='{cmd} {args}\n'.format(cmd=cmd, args=' '.join(sys_args))

    result = run_command(command)
    if result:
        if key:
            send_data(API_ENDPOINT, result, key)
            exit(RETURN_CODE_SUCCESS)
        else:
            handle_normally(result)
            exit(RETURN_CODE_SUCCESS)

    exit(1)
