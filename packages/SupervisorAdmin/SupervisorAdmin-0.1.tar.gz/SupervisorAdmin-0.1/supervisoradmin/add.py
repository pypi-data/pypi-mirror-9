#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
add supervisor jobs
"""

# imports
import argparse
import os
import shlex
import subprocess
import sys
import time

# module globals
__all__ = ['main', 'SupervisorAdminParser']
SUPERVISOR_CONF = '/etc/supervisor/conf.d'

template = """[program:{name}]
command={command}
autorestart=true
redirect_stderr=true
startretries={retries}
stopasgroup=true
stopwaitsecs=180
user={user}
"""

def basename(filename):
    return os.path.splitext(os.path.basename(filename))[0]

class SupervisorAdminParser(argparse.ArgumentParser):
    """CLI option parser"""
    def __init__(self, **kwargs):
        kwargs.setdefault('formatter_class', argparse.RawTextHelpFormatter)
        kwargs.setdefault('description', __doc__)
        argparse.ArgumentParser.__init__(self, **kwargs)
        self.add_argument('command',
                          help="command to add")
        self.add_argument('-n', '--name', dest='name',
                          help="name of program; by default taken from command")
        self.add_argument('-u', '--user', dest='user', default='root',
                          help="run program as this user [DEFAULT: %(default)s]")
        self.add_argument('--retries', dest='retries',
                          type=int, default=100,
                          help="number of retries [DEFAULT: %(default)s]")
        self.add_argument('-o', '--output', dest='output',
                          type=argparse.FileType('w'),
                          nargs='?',
                          const=sys.stdout,
                          help="output configuration and exit [DEFAULT: %(default)s]")
        self.options = None

    def parse_args(self, *args, **kw):
        options = argparse.ArgumentParser.parse_args(self, *args, **kw)
        self.validate(options)
        self.options = options
        return options

    def validate(self, options):
        """validate options"""

def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line options
    parser = SupervisorAdminParser()
    options = parser.parse_args(args)

    # get command
    command = shlex.split(options.command)
    if not command:
        parser.error("Please supply a command")

    # name
    name = options.name or basename(command[0])

    # output configuration file
    output = options.output or open(os.path.join(SUPERVISOR_CONF, '{}.conf'.format(name)), 'w')

    output.write(template.format(name=name,
                                 user=options.user,
                                 retries=options.retries,
                                 command=options.command))
    output.close()

    if options.output is None:
        # update the supervisor state
        subprocess.check_call(['sudo', 'supervisorctl', 'update'])

if __name__ == '__main__':
    main()
