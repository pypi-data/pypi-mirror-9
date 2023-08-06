# Copyright Louis Paternault 2015
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Command line options"""

import argparse
import logging
import os
import textwrap

import evariste
from evariste import VERSION

LOGGER = logging.getLogger(evariste.__name__)

def _setup_type(name):
    """Check the argument and return its value.

    The argument must be an existing file.
    """
    if not os.path.exists(name):
        raise argparse.ArgumentTypeError(
            "File '{}' does not exist.".format(name)
            )
    if not os.path.isfile(name):
        raise argparse.ArgumentTypeError(
            "File '{}' is not a directory.".format(name)
            )
    return name

class Options:
    """Namespace of command line options."""

    _verbose = 1
    _logging_level = {
        0: 100, # Quiet
        1: 30, # Warning
        2: 20, # Info
        3: 15, # Details (custom level)
        4: 10, # Debug
        }

    def __str__(self):
        return str(dict([
            (attr, getattr(self, attr))
            for attr in dir(self)
            if not attr.startswith("_")
            ]))

    @property
    def verbose(self):
        """Get verbose level"""
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        """Set verbose level (if not quiet)"""
        if self._verbose != 0:
            self._verbose = value
            LOGGER.setLevel(self._logging_level.get(self._verbose, 0))

    @property
    def quiet(self):
        """Is --quiet set?"""
        return self.verbose == 0

    @quiet.setter
    def quiet(self, dummy):
        """Set ---quiet"""
        self.verbose = 0

def commandline_parser():
    """Return a command line parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Recursively compile files in a directory, and render result."
            ),
        formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument(
        '--version',
        help='Show version',
        action='version',
        version='%(prog)s ' + VERSION
        )

    parser.add_argument(
        "-v", "--verbose",
        help='Verbose. Repeat for more details.',
        action='count',
        default=0,
        )

    parser.add_argument(
        "-q", "--quiet",
        help='Quiet. Does not print anything to standard output.',
        action='store_true',
        default=False,
        )

    parser.add_argument(
        'setup',
        metavar="SETUP",
        help=textwrap.dedent("""
            Setup file to process.
            """),
        type=_setup_type,
        )

    # TODO option -B --always-make
    # TODO option -n --dry-run
    # TODO option -r --render
    # TODO option -e --error stop on error
    # TODO option -j --jobs number of jobs

    return parser

def get_options():
    """Return the namespace of command line options."""
    return commandline_parser().parse_args(namespace=Options())
