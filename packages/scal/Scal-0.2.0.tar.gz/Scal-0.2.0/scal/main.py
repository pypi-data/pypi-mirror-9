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

"""Produce a calendar."""

import logging
import sys

from scal import calendar, errors, options
from scal.template import generate_tex
import scal

LOGGER = logging.getLogger(scal.__name__)
LOGGER.addHandler(logging.StreamHandler())

def main():
    """Main function"""
    arguments = options.commandline_parser().parse_args(sys.argv[1:])
    try:
        inputcalendar = calendar.Calendar(arguments.FILE[0])
    except errors.ConfigError as error:
        LOGGER.error("Configuration error in file {}: {}".format(
            arguments.FILE[0].name,
            error,
            ))
        sys.exit(1)
    print(generate_tex(inputcalendar, arguments.template, arguments.weeks))

if __name__ == "__main__":
    main()
