#!/usr/bin/env python3

# Copyright Louis Paternault 2011-2014
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Test of calendar parser and renderer"""
# pylint: disable=too-few-public-methods

import glob
import os
import io
import unittest
import sys

from scal import calendar, errors
from scal.template import generate_tex

class ParserRenderer(unittest.TestCase):
    """Test .scl files renderer"""

    maxDiff = None

    def __init__(self, methodname="runTest", basename=None):
        super().__init__(methodname)
        self.basename = basename

    def shortDescription(self):
        return "Parsing file '{}.scl'.".format(self.basename)

    def runTest(self):
        """Test scl output."""
        # pylint: disable=invalid-name

        if self.basename is None:
            return
        with open("{}.scl".format(self.basename), 'r', encoding='utf8') as sourcefile:
            with open("{}.tex".format(self.basename), 'r', encoding='utf8') as expectfile:
                self.assertMultiLineEqual(
                    generate_tex(calendar.Calendar(sourcefile)).strip(),
                    expectfile.read().strip(),
                    )

class TestErrors(unittest.TestCase):
    """Test some errors"""

    def test_empty(self):
        """Test parsing an empty scl file."""
        self.assertRaises(
            errors.ConfigError,
            calendar.Calendar,
            io.StringIO(""),
            )

def load_tests(dummy_loader, tests, dummy_pattern, files=None):
    """Load several tests given test files present in the directory."""
    # Load all scl files as tests
    if not files:
        files = glob.glob(os.path.join(
            os.path.dirname(__file__),
            '*.scl',
            ))
    for scl in sorted(files):
        tests.addTest(ParserRenderer(basename=scl[:-len('.scl')]))
    return tests

def main():
    """Consider that arguments are .scl files to test."""
    runner = unittest.TextTestRunner()
    runner.run(load_tests(None, unittest.TestSuite(), None, sys.argv[1:]))

if __name__ == "__main__":
    main()
