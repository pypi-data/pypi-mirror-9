#!/usr/bin python
# -*- coding: utf8 -*-

# Copyright 2015 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests"""

from __future__ import unicode_literals
from decimal import Decimal
import doctest
import os
import unittest


import papersize

class TestParse(unittest.TestCase):
    """Test parsing related functions."""
    # pylint: disable = invalid-name, star-args

    def assertIterAlmostEqual(self, iter1, iter2):
        """Assert iterators of elements are almost items.

        Both arguments are expected to be iterators of the same size, and
        iterators with the same indexes are checked to be almost equal.
        """


        for left, right in zip(iter1, iter2):
            self.assertAlmostEqual(Decimal(left), Decimal(right))

    def testParseLength(self):
        """Test :func:`papersize.parse_length`."""
        for (args, result) in [
                (("10cm", "mm"), 100),
                (("10in",), 722.7),
            ]:
            self.assertAlmostEqual(
                papersize.parse_length(*args),
                Decimal(result),
                )

        self.assertRaises(
            papersize.CouldNotParse,
            papersize.parse_length,
            "cm"
            )

    def testParseCouple(self):
        """Test :func:`papersize.parse_couple`."""
        for (args, result) in [
                (("10cmx1mm",), (284.5275591, 2.845275591)),
                (("10cmx1mm", "mm"), (100, 1)),
                (("10cm 1mm", "mm"), (100, 1)),
                (("10cm×1mm", "mm"), (100, 1)),
                (("2pc x 3dd", "pt"), (24, 3.21)),
            ]:
            self.assertIterAlmostEqual(
                papersize.parse_couple(*args),
                result,
                )

        self.assertRaises(
            papersize.CouldNotParse,
            papersize.parse_papersize,
            "2cmx2cm 2cm"
            )

    def testParsePaperSize(self):
        """Test :func:`papersize.parse_papersize`."""
        for (args, result) in [
                (("a4", "cm"), (21, 29.7)),
                (("20cm x 1mm", "cm"), (20, 0.1)),
                (("quarto", ), (650.43, 794.97)),
            ]:
            self.assertIterAlmostEqual(
                papersize.parse_papersize(*args),
                result,
                )

        self.assertRaises(
            papersize.CouldNotParse,
            papersize.parse_papersize,
            "Hello, world!"
            )

    def testConvertLength(self):
        """Test :func:`papersize.convert_length`."""
        for (args, result) in [
                ((10, "cm", "mm"), 100),
                ((1, "mm", "pt"), 2.845275591),
            ]:
            self.assertAlmostEqual(
                papersize.convert_length(*args),
                Decimal(result),
                )

class TestOrientation(unittest.TestCase):
    """Test orientation related tools."""
    # pylint: disable = invalid-name, star-args

    def testPortraitLandscape(self):
        """Test portrait/landscape functions."""
        self.assertTrue(papersize.is_portrait(10, 11))
        self.assertTrue(papersize.is_portrait(10, 10))
        self.assertFalse(papersize.is_portrait(11, 10))

        self.assertFalse(papersize.is_landscape(10, 11))
        self.assertTrue(papersize.is_landscape(10, 10))
        self.assertTrue(papersize.is_landscape(11, 10))

        self.assertFalse(papersize.is_square(10, 11))
        self.assertTrue(papersize.is_square(10, 10))
        self.assertFalse(papersize.is_square(11, 10))

    def testRotate(self):
        """Test :func:`papersize.rotate` function."""
        self.assertEqual(
            papersize.rotate((10, 11), True),
            (10, 11),
            )
        self.assertEqual(
            papersize.rotate((10, 11), False),
            (11, 10),
            )

        self.assertRaises(
            papersize.UnknownOrientation,
            papersize.rotate,
            (1, 2), "portrait",
            )

def suite():
    """Return a :class:`TestSuite` object, testing all module :mod:`papersize`.
    """
    test_loader = unittest.defaultTestLoader
    return test_loader.discover(os.path.dirname(__file__))

def load_tests(dummy_loader, tests, dummy_pattern):
    """Load tests (unittests and doctests)."""
    # Loading doctests
    tests.addTests(doctest.DocTestSuite(papersize))

    # Unittests are loaded by default

    return tests

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
