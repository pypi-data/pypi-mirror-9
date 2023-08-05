"""
Core functions and classes for FS Nav
"""


from glob import glob
import os
import re

from . import settings


__all__ = ['Aliases', 'count']


class Aliases(dict):

    def __init__(self, *args, **kwargs):

        """
        Reference specific directories on the filesystem via user-defined aliases
        stored in a dictionary-like object.

        One could just store the aliases and directories in a dictionary but they
        should be validated when added.  Furthermore directory locations and names
        are not completely standardized across operating systems.  The default
        aliases found in `fsnav.DEFAULT_ALIASES` are almost identical when loaded
        on every platform but point to slightly different directories.

        In general, treat `Aliases()` as though it was a dictionary.  In order
        to add an alias, set a key equal to a directory.  Aliases must not
        have spaces or punctuation and directories must exist and be executable.

        An instance of `Aliases()` can be created the following ways:

            >>> aliases = Aliases()
            >>> aliases['home'] = '~/'
            >>> aliases['desk'] = '~/Desktop'

            >>> aliases = Aliases(home='~/', desk='~/Desktop')

            >>> aliases = Aliases({'home': '~/', 'desk': '~/Desktop'})

            >>> aliases = Aliases((('home', '~/'), ('desk', '~/Desktop')))

            >>> print(aliases)
            Aliases({'home': '/Users/wursterk/', 'desk': '/Users/wursterk/Desktop'})

        Aliases can then be used for navigation, most notably via the included
        commandline utility ``nav``.  See ``nav --help`` for more information

            >>> os.chdir(aliases['home'])
            >>> os.getcwd()
            '~/'
        """

        dict.__init__(self)

        # Call update to load items - it already handles the syntax for the following
        # Aliases(alias='path')
        # Aliases(
        self.update(*args, **kwargs)

    def __repr__(self):

        return "%s(%s)" % (self.__class__.__name__, dict((a, p) for a, p in self.items()))

    __str__ = __repr__

    def __enter__(self):

        """
        Included to enable contextmanager syntax - doesn't do any setup
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        """
        Included to enable contextmanager syntax - doesn't do any teardown
        """

        pass

    def __setitem__(self, alias, path):

        """
        Enable ``Aliases[alias] = path`` syntax with the necessary validations.
        A valid `alias` does not contain spaces or punctuation and must match
        the regex defined in `fsnav.settings.ALIAS_REGEX`.  A valid `path` must
        exist and be executable.  Note that `~/` is expanded but `*` wildcards
        are not supported.

        Raises
        ------
        ValueError
            Invalid alias
        KeyError
            Invalid path

        Returns
        -------
        None
        """

        # ave to check for None before expanduser() otherwise an AttributeError is raised
        if path is None:
            raise ValueError("Path cannot be NoneType")
        else:
            path = os.path.expanduser(path)

        # Validate the alias
        if re.match(settings.ALIAS_REGEX, alias) is None:
            raise KeyError("Aliases can only contain alphanumeric characters and '-' or '_': '%s'" % alias)

        # Validate the path
        elif not os.path.isdir(path) and not os.access(path, os.X_OK):
            raise ValueError("Can't access path: '%s'" % path)

        # Alias and path passed validate - add
        else:
            # Forces all non-overridden methods that normally call dict.__setitem__ to call Aliases.__setitem__() in
            # order to take advantage of the alias and path validation
            super(Aliases, self).__setitem__(alias, path)

    def as_dict(self):

        """
        Return the dictionary containing aliases and paths as an actual dictionary

        Returns
        -------
        dict
        """

        return dict(self)

    def setdefault(self, alias, path=None):

        """
        Overrides dict.setdefault() to force usage of new self.__setitem__() method

        Returns
        -------
        str
            Path assigned to alias
        """

        try:
            self[alias]
        except KeyError:
            self[alias] = path
        return self[alias]

    def update(self, alias_iterable=None, **alias_path):

        """
        Overrides dict.update() to force usage of new self.__setitem__()

        Returns
        -------
        None
        """

        if alias_iterable and hasattr(alias_iterable, 'keys'):
            for alias in alias_iterable:
                self[alias] = alias_iterable[alias]
        elif alias_iterable and not hasattr(alias_iterable, 'keys'):
            for (alias, path) in alias_iterable:
                self[alias] = path
        for alias, path in alias_path.items():
            self[alias] = path

    def copy(self):

        """
        Creates a copy of `Aliases()` and all contained aliases and paths

        Returns
        -------
        Aliases
        """

        return Aliases(**self.as_dict())

    def user_defined(self):

        """
        Extract user-defined aliases from an `Aliases()` instance

        Returns
        -------
        Aliases
            All user-defined aes
        """

        return Aliases(
            {a: p for a, p in self.items() if a not in settings.DEFAULT_ALIASES or p != settings.DEFAULT_ALIASES[a]})

    def default(self):

        """
        Extract aliases defined by FS Nav on import

        Returns
        -------
        Aliases
            Default aliases
        """

        return Aliases(
            {a: p for a, p in self.items() if a in settings.DEFAULT_ALIASES and p == settings.DEFAULT_ALIASES[a]})


def count(items_to_count):

    """
    Count files and directories on the commandline.  Performs validation
    and shell expansion so you don't have to.

    Parameters
    ----------
    items_to_count : list or tuple
        List of paths to be counted.  Can contain ``*`` wildcards or ``~/``.
    """

    # Expand all * wildcards and ~/ references
    expanded = []
    for path in items_to_count:
        if '~' in path:
            path = os.path.expanduser(path)
        for p in glob(path):
            expanded.append(p)

    return len(set([p for p in expanded if os.path.exists(p)]))
