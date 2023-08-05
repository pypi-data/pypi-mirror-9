#!/usr/bin/python
# -*- coding: utf8 -*-

import aiqpy
import sys
import pprint
import atexit
import click

try:
    import readline
    import rlcompleter
except ImportError:
    pass
else:
    readline.parse_and_bind("tab: complete")


class LineInfo(object):
    def __init__(self):
        pass

    def __str__(self):
        org = platform.active_organization
        return platform.username + '@' + sys.argv[1] + '/' + org + '> '


def pphook(value):
    if value:
        local_namespace['_'] = value
        pprint.pprint(value)


@atexit.register
def logout():
    try:
        platform.logout()
    except NameError:
        # Platform is not instansiated, no need to log out
        pass


@click.command()
@click.argument('profile')
@click.argument('command', required=False)
@click.option('--no-pretty-print',
              '-npp',
              is_flag=True,
              default=False,
              help='Disable pretty printing of output')
def main(profile, command, no_pretty_print):
    global platform
    import code

    try:
        platform = aiqpy.Connection(profile=profile)
    except aiqpy.exceptions.LoginError as error:
        click.echo(error.message)
        exit()

    platform_functions = {
        name: getattr(platform, name) for name in dir(platform)
        if not name.startswith('_')
    }

    local_namespace.update(locals())
    local_namespace.update(platform_functions)

    if not no_pretty_print:
        sys.displayhook = pphook

    if command:
        result = eval(command)

        if not no_pretty_print:
            result = pphook(result)

        click.echo(result)
    else:
        sys.ps1 = LineInfo()

        code.InteractiveConsole(locals=local_namespace) \
            .interact(banner='AIQ Terminal')

local_namespace = locals()

if __name__ == '__main__':
    main()
