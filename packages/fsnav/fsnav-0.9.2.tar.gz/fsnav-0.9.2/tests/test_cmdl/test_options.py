"""
Unittests: benthos.cmdl.options
"""


import unittest

from fsnav.cmdl import options


class TestParseKeyVals(unittest.TestCase):

    """
    benthos.cli.options.parse_key_vals()
    """

    def test_parse(self):

        # Turn ['k1=v1', 'k2=v2'] into {'k1': 'v1', 'k2': 'v2'}
        pairs = ['k1=v1', 'k2=v2']
        expected = {'k1': 'v1', 'k2': 'v2'}
        self.assertDictEqual(expected, options.parse_key_vals(pairs))

    def test_exception(self):

        # Make sure appropriate exceptions are raised
        self.assertRaises(ValueError, options.parse_key_vals, ['no_equals'])
