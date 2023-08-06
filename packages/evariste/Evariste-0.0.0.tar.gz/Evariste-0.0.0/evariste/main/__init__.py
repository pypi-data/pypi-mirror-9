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

"""Command line client to :mod:`evariste`"""

import logging
import sys

from evariste import errors, tree, renderer
from evariste.action import load_actions
from evariste.main.options import get_options
from evariste.rcs import git
from evariste.setup import Setup
import evariste

LOGGER = logging.getLogger(evariste.__name__)
LOGGER.addHandler(logging.StreamHandler())
logging.addLevelName(15, "DETAIL")

def main():
    """Main function"""
    arguments = get_options()
    try:
        LOGGER.info("Reading setup…")
        setup = Setup.from_file(arguments.setup) # pylint: disable=no-member
        LOGGER.info("Building directory tree…")
        directory = tree.build_tree(
            git.Git(setup['setup']['source']),
            setup,
            )
        LOGGER.info("Compiling…")
        directory.compile_root(load_actions(setup))

        renderers = evariste.renderer.load_renderers(setup)
        for keyword in setup["renderer"]["plugins"]:
            LOGGER.info("Rendering {}…".format(keyword))
            print(renderers.match(keyword).render(directory))
    except errors.EvaristeError as error:
        LOGGER.error("Error: " + str(error))
        sys.exit(1)
