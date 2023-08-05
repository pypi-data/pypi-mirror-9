FS Nav
======

[![Build Status](https://travis-ci.org/geowurster/FS-Nav.svg?branch=master)](https://travis-ci.org/geowurster/FS-Nav) [![Coverage Status](https://coveralls.io/repos/geowurster/FS-Nav/badge.svg?branch=master)](https://coveralls.io/r/geowurster/FS-Nav?branch=master)

File System Navigation shortcuts for the commandline


Overview
--------

In short, `FS Nav` allows users to navigate to directories by typing in a
single word and pressing return.

Learning to use the commandline can be daunting but required in order to use
specific tools.  The goal of `FS Nav` is to make navigating to common locations
easier and slightly more intuitive both for new users and those that find
themselves navigating complex file systems.  

When set up `FS Nav` allows the user to navigate to the `desktop` like so:

    $ pwd
    /Users/geowurster
    $ desktop
    $ pwd
    /Users/geowurster/Desktop

NOTE: The above functionality does not yet support the `Windows` commandline
but works with [cygwin](http://cygwin.org).


Commandline Utilities
---------------------

#### nav ####

The `nav` utility is responsible for driving the file system navigation.  There
are several sub-commands, the most important of which is `nav get`, which
prints out an alias's path.

    $ nav get home
    /Users/geowurster

In order to see a list of all currently recognized aliases, use `nav aliases`.
    
    $ nav aliases
    {'applications': '/Applications',
    'desk': '/Users/geowurster/Desktop',
    'desktop': '/Users/geowurster/Desktop',
    ...}
    
User defined aliases can be added with `nav config addalias`.  New aliases can
be added and default aliases can be re-defined but default aliases can not be
fully deleted.
    
    $ nav config addalias fsnav=~/github/FS-Nav desk=~/github
    $ nav get fsnav
    /Users/geowurster/github/FS-Nav
    
    # Re-assign a default alias
    $ nav get desk
    /Users/geowurster/github
    
    # Deleting a re-assigned default alias makes it revert to its original value
    $ nav config deletealias desk
    $ nav get desk
    /Users/geowurster/Desktop

See `nav config --help` for additional commands.


#### count ####

A bonus utility of sorts - quickly count items on the file system.  Handles
wildcard expansion and only counts paths that actually exist.

    $ cd github/FS-Nav
    $ count *
    9
    $ count * fsnav/*
    19


Installation
------------

Via pip:

    $ pip install fsnav

Master branch:

    $ git clone https://github.com/geowurster/FS-Nav
    $ cd FS-Nav
    $ python setup.py install


Setup
-----

Once installed, `FS Nav` requires the user to add a startup command to their
profile.  In order to just try `FS-Hav`, do `eval $(nav startup generate)`.

Mac, Linux, Cygwin, etc.
    
    $ nav startup profile >> ~/.bash_profile
    $ source ~/.bash_profile

Windows commandline "one-word navigation" is not yet supported.

Verify that everything is working properly with:
    
    $ cd ~/
    $ pwd
    /Users/geowurster
    $ desktop
    $ pwd
    /Users/geowurster/Desktop


Python API
----------

For detailed information about a given object, do `help(<object>)`.

#### Loading aliases ####

Load only the default aliases `FS-Nav` defines on import.

    from pprint import pprint
    
    import fsnav
    
    aliases = fsnav.Aliases(fsnav.DEFAULT_ALIASES)

#### Working with the configfile ####

The configfile is `JSON` encoded and currently only contains user-defined
aliases in a section called `aliases`.  The path to the configfile is stored
in `fsnav.CONFIGFILE` and the name of the section containing the aliases is
stored in `fsnav.CONFIGFILE_ALIAS_SECTION`.
    
    {
        'aliases': {
            'fsnav': '/Users/geowurster/github/FS-Nav/'
        }
    }

Load the aliases in the configfile:

    import json
    
    import fsnav
    
    with open(fsnav.CONFIGFILE) as f:
        cfg_aliases = json.load(f)[fsnav.CONFIGFILE_ALIAS_SECTION]
    
    aliases = fsnav.Aliases(cfg_aliases)

#### Loading multiple sets of aliases ####

Note that the `list()` call is required for Python 3.  Note that the aliases
from the configfile are loaded last in order to overwrite any default aliases
with the same name.

    import fsnav
    
    all_aliases = list(fsnav.DEFAULT_ALIASES.items()) + list(cfg_aliases.items()) 
    aliases = fsnav.Aliases(all_aliases.copy())

#### The `Aliases()` class ####

`Aliases()` subclasses `dict()` but overrides a few methods for `alias` and
`path` validation.  A handful of `FS Nav` specific methods are also present.
Generally, an instance of `Aliases()` acts just like an instance of `dict()`.

    import fsnav
    
    aliases = fsnav.Aliases()
    new_aliases = {'desk': '~/Desktop', 'home': '~/'}
    
    for a, p in new_aliases.items():
        aliases[a] = p
    assert sorted(new_aliases.keys()) == sorted(aliases.keys())
    
    del aliases['desk']
    assert 'desk' not in aliases
    
    aliases.update({'desk': '~/Desktop')
    assert aliases['desk'] == new_aliases['desk']

For more information see `help(fsnav.Aliases)`

#### Counting items on the file system ####

The `count` utility directly calls this function.
    
    import fsnav
    
    num_files = fsnav.count('/Users/geowurster/github/FS-Nav/*')
