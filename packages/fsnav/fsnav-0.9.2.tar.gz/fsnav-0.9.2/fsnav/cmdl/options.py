"""
Options and flags needed by multiple commandline utilities
"""


import click

import fsnav.settings


def print_version(ctx, param, value):

    """
    Print version and exit

    Parameters
    ----------
    ctx : click.Context or None
        Parent context
    param : str or None
        Parameter for option
    value : str
        Flag, option, or argument (in this case `--version`)
    """

    if not value or ctx.resilient_parsing:
        return None

    click.echo(fsnav.settings.__version__)
    ctx.exit()


def print_license(ctx, param, value):

    """
    Print license and exit

    Parameters
    ----------
    ctx : click.Context or None
        Parent context
    param : str or None
        Parameter for option
    value : str
        Flag, option, or argument (in this case `--license`)
    """

    if not value or ctx.resilient_parsing:
        return None

    click.echo(fsnav.settings.__license__)
    ctx.exit()


def parse_key_vals(key_vals):

    """
    Parse `KEY=VAL` pairs collected from the commandline
    Turns: ``['k1=v1', 'k2=v2']``
    Into: ``{'k1': 'v1', 'k2': 'v2'}``
    Parameters
    ----------
    key_vals : tuple or list
    Raises
    ------
    ValueError
        Key=val pair does not contain an '='
    Returns
    -------
    dict
        Parsed {'key': 'val'} pairs
    """

    for pair in key_vals:
        if '=' not in pair:
            raise ValueError("Key=val pair does not contain an '=': {}".format(pair))

    return dict(pair.split('=') for pair in key_vals)


version = click.option('--version', is_flag=True, callback=print_version,
                       expose_value=False, is_eager=True, help="Print version")


license = click.option('--license', is_flag=True, callback=print_license,
                       expose_value=False, is_eager=True, help="Print license")


no_pretty = click.option('-np', '--no-pretty', is_flag=True,
                         help="Don't format output")
