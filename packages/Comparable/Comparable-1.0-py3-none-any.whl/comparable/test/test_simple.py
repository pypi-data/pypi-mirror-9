#!/usr/bin/env python

"""Tests for the comparable.simple module."""

import logging
import unittest

from comparable.simple import Number, Text, TextEnum, TextTitle

from comparable.test import TestCase, settings


class TestNumber(TestCase):  # pylint: disable=R0904

    """Integration tests for the Number class."""  # pylint: disable=C0103

    def test_identical(self):
        """Verify two identical numbers can be compared."""
        a = Number(42)
        b = Number(42)
        self.assertComparison(a, b, True, True, 1.00)

    def test_different(self):
        """Verify two different numbers can be compared."""
        a = Number(1)
        b = Number(42)
        self.assertComparison(a, b, False, False, 0.02)

    def test_one_zero(self):
        """Verify zero can be compared with another number."""
        a = Number(0)
        b = Number(42)
        self.assertComparison(a, b, False, False, 0.00)

    def test_both_zero(self):
        """Verify two zero can be compared."""
        a = Number(0)
        b = Number(0)
        self.assertComparison(a, b, True, True, 1.00)

    def test_init_invalid(self):
        """Verify that a number can only be positive."""
        self.assertRaises(ValueError, Number, -1)

    def test_str(self):
        """Verify a Number can be converted to a string."""
        self.assertEqual("42.0", str(Number(42.0)))

    def test_bool(self):
        """verify a Number can be converted to a boolean."""
        self.assertTrue(Number(42))
        self.assertFalse(Number(0))

    def test_threshold(self):
        """Verify the Number threshold is correct."""
        self.assertTrue(Number(100) %
                        Number(99.9))
        self.assertFalse(Number(100) %
                         Number(99.8))


class TestText(TestCase):  # pylint: disable=R0904

    """Integration tests for the Text class."""  # pylint: disable=C0103

    def test_identical(self):
        """Verify two identical texts can be compared."""
        a = Text("abc123")
        b = Text("abc123")
        self.assertComparison(a, b, True, True, 1.00)

    def test_different(self):
        """Verify two different texts can be compared."""
        a = Text("abc123")
        b = Text("def456")
        self.assertComparison(a, b, False, False, 0.00)

    def test_close(self):
        """Verify two similar texts can be compared."""
        a = Text("abcdefghijklmnopqrstuvwzyz")
        b = Text("Abcdefghijklmnopqrstuvwzyz")
        self.assertComparison(a, b, False, True, 0.96)

    def test_one_empty(self):
        """Verify an empty text can be compared to a text."""
        a = Text("")
        b = Text("def456")
        self.assertComparison(a, b, False, False, 0.00)

    def test_both_empty(self):
        """Verify two empty texts can be compared."""
        a = Text("")
        b = Text("")
        self.assertComparison(a, b, True, True, 1.00)

    def test_threshold(self):
        """Verify the Text threshold is correct."""
        self.assertTrue(Text("Hello, world!") %
                        Text("hello world"))
        self.assertFalse(Text("Hello, world!") %
                         Text("hello worlds"))


class TestEnum(TestCase):  # pylint: disable=R0904

    """Integration tests for the TextEnum class."""  # pylint: disable=C0103

    def test_identical(self):
        """Verify two identical text enums can be compared."""
        a = TextEnum("abc123")
        b = TextEnum("abc123")
        self.assertComparison(a, b, True, True, 1.00)

    def test_different(self):
        """Verify two different text enums can be compared."""
        a = TextEnum("abc123")
        b = TextEnum("def456")
        self.assertComparison(a, b, False, False, 0.00)

    def test_close(self):
        """Verify two similar text enums can be compared."""
        a = TextEnum("abcdefghijklmnopqrstuvwzyz")
        b = TextEnum("Abcdefghijklmnopqrstuvwzyz")
        self.assertComparison(a, b, False, True, 1.00)

    def test_threshold(self):
        """Verify the TextEnum threshold is correct."""
        self.assertTrue(TextEnum("Hello, world!") %
                        TextEnum("hello, world!"))
        self.assertFalse(TextEnum("Hello, world!") %
                         TextEnum("Hello, world"))


class TestTextTitle(TestCase):  # pylint: disable=R0904

    """Integration tests for the TextTitle class."""  # pylint: disable=C0103

    def test_identical(self):
        """Verify two identical text titles can be compared."""
        a = TextTitle("The Cat and the Hat")
        b = TextTitle("The Cat and the Hat")
        self.assertComparison(a, b, True, True, 1.00)

    def test_different(self):
        """Verify two different text titles can be compared."""
        a = TextTitle("The Cat and the Hat")
        b = TextTitle("A Clockwork Orange")
        self.assertComparison(a, b, False, False, 0.32)

    def test_close(self):
        """Verify two similar text titles can be compared."""
        a = TextTitle("The Cat and the Hat")
        b = TextTitle("The Cat & The Hat")
        self.assertComparison(a, b, False, True, 1.00)

    def test_threshold(self):
        """Verify the TextTitle threshold is correct."""
        self.assertTrue(TextTitle("The Cat and the Hat") %
                        TextTitle("cat an' the hat"))
        self.assertFalse(TextTitle("The Cat and the Hat") %
                         TextTitle("cat and hat"))


if __name__ == '__main__':
    logging.basicConfig(format=settings.DEFAULT_LOGGING_FORMAT,
                        level=settings.DEFAULT_LOGGING_LEVEL)
    unittest.main(verbosity=0)
