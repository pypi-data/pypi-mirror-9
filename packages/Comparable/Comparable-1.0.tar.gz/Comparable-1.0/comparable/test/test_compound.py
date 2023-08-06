#!/usr/bin/env python

"""Tests for the comparable.compound module."""

import logging
import unittest

from comparable.simple import Text
from comparable.compound import Group

from comparable.test import TestCase, settings


class TestGroup(TestCase):  # pylint: disable=R0904

    """Integration tests for the Items class."""  # pylint: disable=C0103

    def test_attributes(self):
        """Verify __getattr__ behaves correctly."""
        self.assertRaises(AttributeError, getattr, Group([]), 'fake')
        self.assertRaises(AttributeError, getattr, Group([]), 'itemA')
        self.assertRaises(AttributeError, getattr, Group([]), 'item1')

    def test_identical(self):
        """Verify two identical groups can be compared."""
        a = Group([Text("abc"), Text("123")])
        b = Group([Text("abc"), Text("123")])
        self.assertComparison(a, b, True, True, 1.00)

    def test_different_contents(self):
        """Verify two different groups can be compared."""
        a = Group([Text("abc"), Text("123")])
        b = Group([Text("def"), Text("456")])
        self.assertComparison(a, b, False, False, 0.0)

    def test_different_lengths(self):
        """Verify two different sized groups can be compared."""
        a = Group([Text("abc"), Text("123")])
        b = Group([Text("abc"), Text("123"), Text("$"), Text("#")])
        self.assertComparison(a, b, False, False, 0.5)

    def test_first_empty(self):
        """Verify an empty group and group can be compared."""
        a = Group([])
        b = Group([Text("abc"), Text("123")])
        self.assertComparison(a, b, False, False, 0.0)

    def test_second_empty(self):
        """Verify a group and empty group can be compared."""
        a = Group([Text("abc"), Text("123")])
        b = Group([])
        self.assertComparison(a, b, False, False, 0.0)

    def test_both_empty(self):
        """Verify two empty groups can be compared."""
        a = Group([])
        b = Group([])
        self.assertComparison(a, b, True, True, 1.0)


if __name__ == '__main__':
    logging.basicConfig(format=settings.DEFAULT_LOGGING_FORMAT,
                        level=settings.DEFAULT_LOGGING_LEVEL)
    unittest.main(verbosity=0)
