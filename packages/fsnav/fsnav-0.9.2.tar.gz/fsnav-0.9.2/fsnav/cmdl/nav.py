"""
FS Nav utility: nav
"""


import json
import os
import pprint
import sys

import click

import fsnav
from fsnav.cmdl import options


# =========================================================================== #
#   Command group: main
# =========================================================================== #

@click.group()
@click.option(
    '-c', '--configfile', type=click.Path(), default=fsnav.settings.CONFIGFILE,
    help="Specify configfile"
)
@click.option(
    '-nld', '--no-load-default', is_flag=True,
    help="Don't load default aliases"
)
@click.option(
    '-nlc', '--no-load-configfile', is_flag=True,
    help="Don't load the configfile"
)
@options.version
@options.license
@click.pass_context
def main(ctx, configfile, no_load_default, no_load_configfile):

    """
    FS Nav commandline utility
    """

    # Store variables needed elsewhere
    ctx.obj = {
        'no_load_default': no_load_default,
        'no_load_configfile': no_load_configfile,
        'cfg_path': configfile,
        'loaded_aliases': fsnav.Aliases({}),
        'cfg_content': None
    }

    # MAY NEED TO ADD A MORE VERBOSE WARNING HERE
    # Cache all the configfile content
    # Try-except handles configfiles that are completely empty
    try:
        if os.access(configfile, os.R_OK):
            with open(configfile) as f:
                ctx.obj['cfg_content'] = json.loads(f.read())
    except ValueError:
        pass

    # Load the default and configfile aliases according to the above settings
    if not no_load_default:
        for a, p in fsnav.settings.DEFAULT_ALIASES.items():
            ctx.obj['loaded_aliases'][a] = p
    if ctx.obj['cfg_content'] is not None and not no_load_configfile and os.access(configfile, os.R_OK):
        for a, p in ctx.obj['cfg_content'][fsnav.settings.CONFIGFILE_ALIAS_SECTION].items():
            ctx.obj['loaded_aliases'][a] = p


# --------------------------------------------------------------------------- #
#   Command: get
# --------------------------------------------------------------------------- #

@main.command()
@click.argument(
    'alias', required=True,
)
@click.pass_context
def get(ctx, alias):

    """
    Print out the path assigned to an alias
    """

    try:
        click.echo(ctx.obj['loaded_aliases'][alias])
        sys.exit(0)
    except KeyError:
        click.echo("ERROR: Invalid alias: %s" % alias, err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Command: aliases
# --------------------------------------------------------------------------- #

@main.command()
@options.no_pretty
@click.pass_context
def aliases(ctx, no_pretty):

    """
    Print recognized aliases
    """

    try:

        aliases_ = {str(a): str(p) for a, p in ctx.obj['loaded_aliases'].as_dict().items()}
        if no_pretty:
            text = json.dumps(aliases_)
        else:
            text = pprint.pformat(aliases_)
        click.echo(text)
        sys.exit(0)

    except Exception as e:  # pragma no cover
        click.echo(str(e), err=True)
        sys.exit(1)


# =========================================================================== #
#   Command group: startup
# =========================================================================== #

@main.group()
@click.pass_context
def startup(ctx):

    """
    Code needed to enable shortcuts on startup
    """

    pass


# --------------------------------------------------------------------------- #
#   Command: generate
# --------------------------------------------------------------------------- #

@startup.command()
@click.pass_context
def generate(ctx):

    """
    Shell function shortcuts
    """

    try:

        click.echo(' ; '.join(fsnav.fg_tools.generate_functions(ctx.obj['loaded_aliases'])))
        sys.exit(0)

    except Exception as e:  # pragma no cover
        click.echo(str(e), err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Command: profile
# --------------------------------------------------------------------------- #

@startup.command()
@click.pass_context
def profile(ctx):

    """
    Code to activate shortcuts on startup
    """

    try:

        click.echo(fsnav.fg_tools.startup_code)
        sys.exit(0)

    except Exception as e:  # pragma no cover
        click.echo(str(e), err=True)
        sys.exit(1)


# =========================================================================== #
#   Command group: config
# =========================================================================== #

@main.group()
@click.pass_context
def config(ctx):

    """
    Configure FS Nav
    """

    pass


# --------------------------------------------------------------------------- #
#   Command: default
# --------------------------------------------------------------------------- #

@config.command()
@options.no_pretty
@click.pass_context
def default(ctx, no_pretty):

    """
    Print the default aliases
    """

    try:

        default_aliases = {str(a): str(p) for a, p in ctx.obj['loaded_aliases'].default().as_dict().items()}
        if no_pretty:
            text = json.dumps(default_aliases)
        else:
            text = pprint.pformat(default_aliases)
        click.echo(text)
        sys.exit(0)

    except Exception as e:  # pragma no cover
        click.echo(str(e), err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Command: nondefault
# --------------------------------------------------------------------------- #

@config.command()
@options.no_pretty
@click.pass_context
def userdefined(ctx, no_pretty):

    """
    Print user-defined aliases
    """

    try:

        nd_aliases = {str(a): str(p) for a, p in ctx.obj['loaded_aliases'].user_defined().as_dict().items()}
        if no_pretty:
            text = json.dumps(nd_aliases)
        else:
            text = pprint.pformat(nd_aliases)
        click.echo(text)
        sys.exit(0)

    except Exception as e:  # pragma no cover
        click.echo(str(e), err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Command: set
# --------------------------------------------------------------------------- #

@config.command()
@click.argument(
    'alias_path', metavar='alias=path', nargs=-1, required=True,
)
@click.option(
    '-no', '--no-overwrite', is_flag=True,
    help="Don't overwrite configfile if it exists"
)
@click.pass_context
def addalias(ctx, alias_path, no_overwrite):

    """
    Add a user defined alias
    """

    if no_overwrite and os.access(ctx.obj['cfg_path'], os.W_OK):
        click.echo("ERROR: No overwrite is {no_overwrite} and configfile exists: {configfile}".format(
            no_overwrite=no_overwrite, configfile=ctx.obj['cfg_path']), err=True)
        sys.exit(1)

    try:

        aliases_ = ctx.obj['loaded_aliases'].copy()
        for a, p in options.parse_key_vals(alias_path).items():
            aliases_[a] = p
        with open(ctx.obj['cfg_path'], 'w') as f:
            json.dump({fsnav.settings.CONFIGFILE_ALIAS_SECTION: aliases_.user_defined()}, f)
        sys.exit(0)

    except Exception as e:  # pragma no cover
        click.echo(str(e), err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Command: path
# --------------------------------------------------------------------------- #

@config.command()
@click.pass_context
def path(ctx):

    """
    Print the path to the configfile
    """

    try:

        click.echo(ctx.obj['cfg_path'])
        sys.exit(0)

    except Exception as e:  # pragma no cover
        click.echo(str(e), err=True)
        sys.exit(1)


# --------------------------------------------------------------------------- #
#   Command: delete
# --------------------------------------------------------------------------- #

@config.command()
@click.argument(
    'alias', required=True, nargs=-1
)
@click.option(
    '-no', '--no-overwrite', is_flag=True,
    help="Don't overwrite configfile if it exists"
)
@click.pass_context
def deletealias(ctx, alias, no_overwrite):

    """
    Remove an alias from the configfile
    """

    if no_overwrite and os.access(ctx.obj['cfg_path'], os.W_OK):
        click.echo("ERROR: No overwrite is {no_overwrite} and configfile exists: {configfile}".format(
            no_overwrite=no_overwrite, configfile=ctx.obj['cfg_path']), err=True)
        sys.exit(1)

    try:

        aliases_ = fsnav.Aliases({a: p for a, p in ctx.obj['loaded_aliases'].items() if a not in alias})
        with open(ctx.obj['cfg_path'], 'w') as f:
            json.dump({fsnav.settings.CONFIGFILE_ALIAS_SECTION: aliases_.user_defined()}, f)
        sys.exit(0)

    except Exception as e:  # pragma no cover
        click.echo(str(e).message, err=True)
        sys.exit(1)
