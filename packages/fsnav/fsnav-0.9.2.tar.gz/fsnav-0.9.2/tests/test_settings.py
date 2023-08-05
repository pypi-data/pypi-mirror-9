"""
Unittests for: fsnav.settings
"""


import re
import os
import unittest

from fsnav import settings


class TestDefaultAliases(unittest.TestCase):

    def setUp(self):

        # Make sure there's something to test
        self.assertGreater(len(settings.DEFAULT_ALIASES), 0)

    def test_existence(self):

        # Make sure all the default aliases actually exist and are accessible
        for path in settings.DEFAULT_ALIASES.values():
            self.assertTrue(os.path.exists(path))

    def test_validity(self):

        # Failure could mean ``fsnav.core.validate_path()`` and/or ``fsnav.core.validate_alias()`` is broken
        for alias, path in settings.DEFAULT_ALIASES.items():
            self.assertIsNotNone(re.match(settings.ALIAS_REGEX, alias), msg="Alias='{}'".format(alias))
            self.assertTrue(os.path.isdir(path) and os.access(path, os.X_OK), msg="Path='{}'".format(path))

    def test_check_for_invalid(self):

        # The number of aliases explicitly defined in the `settings._${PLATFORM}_ALIASES` dictionary
        # should generally match what ends up in `settings.DEFAULT_ALIASES`.  If the user has modified
        # The default directory names on their system this test will fail

        self.assertDictContainsSubset(
            settings.DEFAULT_ALIASES,
            settings.__dict__['_{norm_plat}_ALIASES'.format(norm_plat=settings.NORMALIZED_PLATFORM.upper())].copy(),
        )
