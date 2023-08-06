"""Tests for the comparable package."""

import os
import logging
import unittest

ENV = 'TEST_INTEGRATION'  # environment variable to enable integration tests
REASON = "'{0}' variable not set".format(ENV)


class TestCase(unittest.TestCase):  # pylint: disable=R0904

    """Common test case class with new assertion methods."""  # pylint: disable=C0103

    def assertComparison(self, a, b, exp_equal, exp_similar, exp_similarity):  # pylint:disable=R0913
        """Fail if objects do not match the expected equality/similarity."""
        logging.info("calculating equality...")
        act_equality = a == b
        logging.info("calculating similarity...")
        act_similarity = a % b
        logging.info("checking expected results...")
        self.assertEqual(exp_equal, bool(act_equality))
        self.assertEqual(exp_similar, bool(act_similarity))
        self.assertAlmostEqual(exp_similarity, act_similarity, 2)


@unittest.skipUnless(os.getenv(ENV), REASON)  # pylint: disable=R0904
class TestIntegration(TestCase):

    """Integration tests for the comparable package."""

    def test_imports(self):
        """Verify package-level imports are working."""
        from comparable import simple
        from comparable.simple import Text
        from comparable import compound
        from comparable.compound import Group
        self.assertEqual(Text("abc"), simple.Text("abc"))
        self.assertEqual(Group(["abc"]), compound.Group(["abc"]))
