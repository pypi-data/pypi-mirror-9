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

"""Abstract class for a renderer with a destination folder."""

import os

from evariste import renderer, errors

class DestRenderer(renderer.Renderer):
    """Abstract class for a renderer with a destination folder."""
    # pylint: disable=too-few-public-methods

    def __init__(self, setup):
        super().__init__(setup)

        self.destdir = self.setup['dest']
        if self.destdir is None:
            self.destdir = self.keyword
        try:
            os.makedirs(self.destdir, exist_ok=True)
        except FileExistsError:
            raise errors.EvaristeError("Cannot create directory '{}'.".format(self.destdir))

    def render(self, tree):
        raise NotImplementedError()
