"""
Unittests for: fsnav.fg_tools
"""


import unittest

import fsnav
from fsnav import fg_tools


class TestFunctions(unittest.TestCase):

    def test_generate_nix_functions(self):
        self.assertIsInstance(fg_tools._generate_nix_functions(fsnav.Aliases({'home': '~/'})), list)

    def test_generate_windows_functions(self):
        self.assertRaises(NotImplementedError, fg_tools._generate_windows_functions, None)

    def test_generate_windows_startup_code(self):
        self.assertRaises(NotImplementedError, fg_tools._generate_windows_startup_code)

    def test_generate_nix_startup_code(self):
        self.assertIsInstance(fg_tools._generate_nix_startup_code(), str)
