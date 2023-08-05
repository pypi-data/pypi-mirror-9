#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_garland
----------------------------------

Tests for `garland` module.
"""

import unittest
import garland

from . import examples
from . import examples as qualfied_examples


class TestReload(unittest.TestCase):
    """
    Basic testing and ensure that tests can be run with patching and without
    in sequence.
    """

    def test_absent_mock(self):
        self.assertIsInstance(examples.dictionary(), list)

    @garland.tinsel('tests.decorators.no_params', 'tests.examples')
    def test_decorated(self):
        self.assertIsInstance(examples.dictionary(), dict)

    def test_no_tinsel(self):
        """Ensure previous test mocking no longer functioning"""
        self.assertIsInstance(examples.dictionary(), list)

    @garland.tinsel('tests.decorators.with_params', 'tests.examples')
    def test_params(self):
        self.assertEqual(examples.world(), "world")

    @garland.tinsel('tests.decorators.with_params', 'tests.examples')
    def test_kwarg_params(self):
        self.assertEqual(examples.bar(), "bar")

    @garland.tinsel('tests.decorators.with_params', 'tests.examples')
    def test_qualified_import(self):
        self.assertEqual(qualfied_examples.bar(), "bar")


if __name__ == '__main__':
    unittest.main()
