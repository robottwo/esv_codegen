"""
Unit tests for the ESV schema package.
"""

from ..schema import Schema
import unittest
import os

def _locate(filename):
    """
    Find the file relative to where the test is located.
    """
    return os.path.join(os.path.dirname(__file__), filename)

class Schema_Test(unittest.TestCase):
    """
    Unit tests for schema parsing.
    """
    def check_invalid(self, basename):
        """
        Workhorse function to check invalid schema files.
        """
        filename = _locate(basename)
        with open(filename) as infile:
            with self.assertRaises(ValueError):
                Schema.parse(infile)

    def test_invalid_schemas(self):
        """
        Test that we catch different types of invalid files.
        """
        self.check_invalid('invalid1.esv')
        self.check_invalid('invalid3.esv')


    def test_simple_schema(self):
        """
        Test that we can create some valid schemas.
        """
        for basename in ('valid1.esv',):
            filename = _locate(basename)
            with open(filename) as infile:
                schema = Schema.parse(infile)
