"""
FS Nav utility: count
"""


import sys

import click

import fsnav
from fsnav.cmdl import options


@click.command()
@options.version
@options.license
@click.argument(
    'paths', metavar='path', nargs=-1, required=True
)
@click.pass_context
def main(ctx, paths):

    """
    Quickly count items on the file system.

    Only paths that exist will be counted
    """

    try:

        click.echo(fsnav.count(paths))
        sys.exit(0)

    except Exception as e:  # pragma no cover
        click.echo(str(e), err=True)
        sys.exit(1)
