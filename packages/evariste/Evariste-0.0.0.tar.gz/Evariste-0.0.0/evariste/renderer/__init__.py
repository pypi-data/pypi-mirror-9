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

"""Render (processed) tree: abstract class."""

import jinja2
import os
import pathlib
import pkg_resources
import tempfile
import textwrap

from evariste import errors, plugins, readme, target

def load_renderers(setup):
    """Return the :class:`PluginLoader`` of renderer plugins."""
    return plugins.PluginLoader(["renderer"], Renderer, setup)

class Renderer(plugins.PluginBase):
    """Abstract tree renderer."""

    plugin_type = ["renderer"]

    plugin_baseclasses = {
        "readme": readme.ReadmeRenderer,
        "target": target.TargetRenderer,
        }

    def priority(self):
        """Return keyword as priority.

        That way, plugins are sorted by name.
        """
        return self.keyword

    def match(self, value):
        """Return ``True`` iff ``value`` is the keyword."""
        return value == self.keyword

    def render(self, tree):
        """Render tree."""
        raise NotImplementedError()

