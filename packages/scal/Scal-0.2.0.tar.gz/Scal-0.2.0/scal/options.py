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

"""Command line options"""

import argparse
import os
import textwrap
import sys

from scal import VERSION
from scal import calendar

def _type_week(text):
    """Check that --week argument is of the right type."""
    try:
        return calendar.parse_weeks(text)
    except KeyError:
        raise argparse.ArgumentTypeError(
            "argument must be one of {{{}}}.".format(
                ", ".join(calendar.WEEK_CHOICES)
                )
            )

def _file_exists(text):
    """Check that file exists."""
    if os.path.exists(text):
        return text
    else:
        raise argparse.ArgumentTypeError(
            "'{}' must be an existing file.".format(text)
            )

def commandline_parser():
    """Return a command line parser."""

    parser = argparse.ArgumentParser(
        description="A year calendar producer.",
        )

    parser.add_argument(
        '--version',
        help='Show version',
        action='version',
        version='%(prog)s ' + VERSION
        )

    parser.add_argument(
        '--weeks', '-w',
        help=textwrap.dedent("""
            Display week numbers : ISO week numbers, number of worked weeks
            since the beginning, or both.
        """),
        type=_type_week,
        default='both',
    )

    parser.add_argument(
        '--template', '-t',
        help='Template to use, if different from default template',
        type=_file_exists,
        default=None,
        metavar="FILE",
        )

    parser.add_argument(
        'FILE',
        help='Configuration file',
        nargs=1,
        type=argparse.FileType('r'),
        default=sys.stdin,
        )

    return parser

