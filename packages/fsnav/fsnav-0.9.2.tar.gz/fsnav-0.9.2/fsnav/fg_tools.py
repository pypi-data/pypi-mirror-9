"""
Commandline function generator tools
"""


from . import settings


def _generate_nix_functions(aliases):

    """
    Generate commandline shortcuts for POSIX systems

    Parameters
    ----------
    aliases : dict or fsnav.core.Aliases
        Dictionary or ``Aliases`` instance from which to generate functions

    Returns
    -------
    list
        Containing the code necessary to create shell functions that act as
          shortcuts to specific directories.
    """

    return ['function %s() { cd "$(%s get %s)" ; }' % (alias, settings.NAV_UTIL, alias) for alias in aliases]


def _generate_windows_functions(aliases):

    """
    **NOT YET IMPLEMENTED**

    Generate commandline shortcuts for Windows

    Parameters
    ----------
    aliases : dict or fsnav.core.Aliases
        Dictionary or ``Aliases`` instance from which to generate functions

    Returns
    -------
    list
        Containing the code necessary to create shell functions that act as
          shortcuts to specific directories.
    """

    raise NotImplementedError("Windows commandline functions are not currently supported")


def _generate_nix_startup_code():

    """
    Add the returned code to your bash profile to automatically generate
    commandline shortcuts every time a new session is started.

    Returns
    -------
    str or unicode
    """

    return """
# == Enable FS Nav shortcuts on startup == #
if [ -x $(which %s) ]; then
    eval $(%s startup generate)
fi
""" % (settings.NAV_UTIL, settings.NAV_UTIL)


def _generate_windows_startup_code():

    """
    **NOT YET IMPLEMENTED**

    Add the returned code to your bash profile to automatically generate
    commandline shortcuts every time a new session is started.

    Returns
    -------
    str or unicode
    """

    raise NotImplementedError("Windows commandline shortcuts are not currently supported")


if settings.NORMALIZED_PLATFORM in ('mac', 'cygwin', 'linux', 'win', 'UNKNOWN'):
    generate_functions = _generate_nix_functions
    startup_code = _generate_nix_startup_code()
elif settings.NORMALIZED_PLATFORM == 'windows':  # pragma no cover
    generate_functions = _generate_windows_functions
    startup_code = _generate_windows_startup_code()
