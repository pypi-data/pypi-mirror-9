"""
Settings and data
"""


import getpass
import os
from os.path import expanduser, join
import sys


__all__ = ['__version__', '__release__', '__author__', '__email__', '__source__', '__license__',
           'DEFAULT_ALIASES', 'CONFIGFILE', 'CONFIGFILE_ALIAS_SECTION', 'NORMALIZED_PLATFORM']


# =========================================================================== #
#   Build information
# =========================================================================== #

__version__ = '0.9.2'
__release__ = '2014-06-28'
__author__ = 'Kevin Wurster'
__email__ = 'wursterk@gmail.com'
__source__ = 'https://github.com/geowurster/FS-Nav'
__license__ = '''
New BSD License

Copyright (c) 2014, Kevin D. Wurster
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* The names of its contributors may not be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''


# =========================================================================== #
#   General settings
# =========================================================================== #

ALIAS_REGEX = "^[\w-]+$"
NAV_UTIL = 'nav'


# =========================================================================== #
#   Platform information
# =========================================================================== #

if 'darwin' in sys.platform.lower().strip():  # pragma no cover
    NORMALIZED_PLATFORM = 'mac'
elif 'cygwin' in sys.platform.lower().strip():  # pragma no cover
    NORMALIZED_PLATFORM = 'cygwin'
elif 'linux' in sys.platform.lower().strip():  # pragma no cover
    NORMALIZED_PLATFORM = 'linux'
elif 'win' in sys.platform.lower().strip():  # pragma no cover
    NORMALIZED_PLATFORM = 'windows'
else:  # pragma no cover
    NORMALIZED_PLATFORM = 'UNKNOWN'


# =========================================================================== #
#   Configfile attributes
# =========================================================================== #

CONFIGFILE = join(expanduser('~'), '.fsnav')
CONFIGFILE_ALIAS_SECTION = 'aliases'


# =========================================================================== #
#   Define aliases for all supported platforms
# =========================================================================== #

_homedir = expanduser('~')
_username = getpass.getuser()

_MAC_ALIASES = {
    'applications':         join(os.sep, 'Applications'),
    'desk':                 join(_homedir, 'Desktop'),
    'desktop':              join(_homedir, 'Desktop'),
    'documents':            join(_homedir, 'Documents'),
    'docs':                 join(_homedir, 'Documents'),
    'downloads':            join(_homedir, 'Downloads'),
    'dl':                   join(_homedir, 'Downloads'),
    'dropbox':              join(_homedir, 'Dropbox'),
    'ghub':                 join(_homedir, 'github'),
    'google_drive':         join(_homedir, 'Google Drive'),
    'gdrive':               join(_homedir, 'Google Drive'),
    'hard_drive':           os.sep,
    'hd':                   os.sep,
    'home':                 _homedir,
    'homedir':              _homedir,
    'images':               join(_homedir, 'Pictures'),
    'movies':               join(_homedir, 'Movies'),
    'music':                join(_homedir, 'Music'),
    'pictures':             join(_homedir, 'Pictures'),
    'public':               join(_homedir, 'Public'),
    'user_applications':    join(_homedir, 'Applications'),
    'user_apps':            join(_homedir, 'Applications'),
    'userapps':             join(_homedir, 'Applications')
}

_DARWIN_ALIASES = _MAC_ALIASES.copy()

_LINUX_ALIASES = {
    'applications':         join(os.sep, 'Applications'),
    'desk':                 join(_homedir, 'Desktop'),
    'desktop':              join(_homedir, 'Desktop'),
    'documents':            join(_homedir, 'Documents'),
    'docs':                 join(_homedir, 'Documents'),
    'downloads':            join(_homedir, 'Downloads'),
    'dl':                   join(_homedir, 'Downloads'),
    'dropbox':              join(_homedir, 'Dropbox'),
    'ghub':                 join(_homedir, 'github'),
    'google_drive':         join(_homedir, 'Google Drive'),
    'gdrive':               join(_homedir, 'Google Drive'),
    'hard_drive':           os.sep,
    'hd':                   os.sep,
    'home':                 _homedir,
    'homedir':              _homedir,
    'images':               join(_homedir, 'Pictures'),
    'movies':               join(_homedir, 'Movies'),
    'music':                join(_homedir, 'Music'),
    'pictures':             join(_homedir, 'Pictures'),
    'public':               join(_homedir, 'Public'),
    'user_applications':    join(_homedir, 'Applications'),
    'user_apps':            join(_homedir, 'Applications'),
    'userapps':             join(_homedir, 'Applications')
}

_CYGWIN_ALIASES = {
    'applications':         join(os.sep, 'cygdrive', 'c', 'Program Files'),
    'desk':                 join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Desktop'),
    'desktop':              join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Desktop'),
    'documents':            join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Documents'),
    'docs':                 join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Documents'),
    'downloads':            join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Downloads'),
    'dl':                   join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Downloads'),
    'dropbox':              join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Dropbox'),
    'ghub':                 join(os.sep, 'cygdrive', 'c', 'Users', _username, 'github'),
    'google_drive':         join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Google Drive'),
    'gdrive':               join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Google Drive'),
    'hard_drive':           join(os.sep, 'cygdrive', 'c'),
    'hd':                   join(os.sep, 'cygdrive', 'c'),
    'home':                 _homedir,
    'homedir':              _homedir,
    'images':               join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Pictures'),
    'movies':               join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Videos'),
    'music':                join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Music'),
    'pictures':             join(os.sep, 'cygdrive', 'c', 'Users', _username, 'Pictures'),
    'public':               join(os.sep, 'cygdrive', 'c', 'Users', 'Public'),
    'winhome':              join(os.sep, 'cygdrive', 'c', 'Users', _username),
    'windowshome':          join(os.sep, 'cygdrive', 'c', 'Users', _username)
}

_WINDOWS_ALIASES = {
    'cyghome':      join('C:', 'cygwin', 'home', _username),
    'cygwinhome':   join('C:', 'cygwin', 'home', _username),
    'cygwin_home':  join('C:', 'cygwin', 'home', _username),
    'desk':         join(_homedir, 'Desktop'),
    'desktop':      join(_homedir, 'Desktop'),
    'documents':    join(_homedir, 'My Documents'),
    'downloads':    join(_homedir, 'Downloads'),
    'dropbox':      join(_homedir, 'Dropbox'),
    'github':       join(_homedir, 'github'),
    'google_drive': join(_homedir, 'Google Drive'),
    'hard_drive':   'C:',
    'hd':           'C:',
    'home':         _homedir,
    'homedir':      _homedir,
    'images':       join(_homedir, 'My Pictures'),
    'top_level':    join('C:'),
    'movies':       join(_homedir, 'My Videos'),
    'music':        join(_homedir, 'My Music'),
    'pictures':     join(_homedir, 'My Pictures'),
    'public':       join(_homedir, 'Public'),
    'system_apps':  join('C:', 'Program Files'),
    'user_apps':    join(_homedir, 'Program Files')
}

_UNKNOWN_ALIASES = {
    'applications':         join(os.sep, 'Applications'),
    'desk':                 join(_homedir, 'Desktop'),
    'desktop':              join(_homedir, 'Desktop'),
    'documents':            join(_homedir, 'Documents'),
    'docs':                 join(_homedir, 'Documents'),
    'downloads':            join(_homedir, 'Downloads'),
    'dl':                   join(_homedir, 'Downloads'),
    'dropbox':              join(_homedir, 'Dropbox'),
    'ghub':                 join(_homedir, 'github'),
    'google_drive':         join(_homedir, 'Google Drive'),
    'gdrive':               join(_homedir, 'Google Drive'),
    'hard_drive':           os.sep,
    'hd':                   os.sep,
    'home':                 _homedir,
    'homedir':              _homedir,
    'movies':               join(_homedir, 'Movies'),
    'music':                join(_homedir, 'Music'),
    'pictures':             join(_homedir, 'Pictures'),
    'public':               join(_homedir, 'Public'),
    'user_applications':    join(_homedir, 'Applications'),
    'user_apps':            join(_homedir, 'Applications'),
    'userapps':             join(_homedir, 'Applications')
}


# =========================================================================== #
#   Expose aliases
# =========================================================================== #

if NORMALIZED_PLATFORM == 'mac':  # pragma no cover
    _DEFAULT_ALIASES = _MAC_ALIASES.copy()
elif NORMALIZED_PLATFORM == 'linux':  # pragma no cover
    _DEFAULT_ALIASES = _LINUX_ALIASES.copy()
elif NORMALIZED_PLATFORM == 'cygwin':  # pragma no cover
    _DEFAULT_ALIASES = _CYGWIN_ALIASES.copy()
elif NORMALIZED_PLATFORM == 'win':  # pragma no cover
    _DEFAULT_ALIASES = _WINDOWS_ALIASES.copy()
else:  # pragma no cover
    _DEFAULT_ALIASES = _UNKNOWN_ALIASES.copy()

# Remove aliases pointing towards non-existent directories
# Python 2.6 does not support direct dictionary comprehension
_DEFAULT_ALIASES = dict(
    (a, p) for a, p in _DEFAULT_ALIASES.copy().items() if os.path.isdir(p) and os.access(p, os.X_OK)
)
DEFAULT_ALIASES = _DEFAULT_ALIASES.copy()
