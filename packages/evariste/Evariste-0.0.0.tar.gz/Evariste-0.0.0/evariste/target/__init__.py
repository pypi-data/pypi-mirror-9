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

"""Target renderers: how should target files be rendered?"""

from evariste import errors, plugins

class TargetRenderer(plugins.PluginBase):
    """Renderer of target (compiled) files."""

    def match(self, dummy):
        """This is the default renderer, that matches everything."""
        return True

    def render(self, tree):
        """Render ``tree``, which is a :class:`tree.File`."""
        raise NotImplementedError()
