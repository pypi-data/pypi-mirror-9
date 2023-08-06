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

"""Master module concerning readme plugins."""

import glob
import os

from evariste import errors, plugins

class CannotRender(errors.EvaristeError):
    """Exception raised when renderer cannot render a given file."""
    pass

class ReadmeRenderer(plugins.PluginBase):
    """Generic class of README renderers, and also a default raw renderer."""
    # pylint: disable=too-few-public-methods, abstract-method

    extensions = []

    plugin_type = ["renderer", "html", "readme"]

    def __init__(self, setup):
        super().__init__(setup)
        # TODO Make it read from the setup file the list of extensions to
        # render as raw.

    def render(self, path, *args, **kwargs):
        """Render the readme file ``path``.
        """
        # pylint: disable=unused-argument, no-self-use
        with open(path) as file:
            return file.read()

    def iter_readme(self, value, directory):
        """Iterave over potential readme files for the path ``value``."""
        if directory:
            yield from self.iter_readme_dir(value)
        else:
            yield from self.iter_readme_file(value)

    def iter_readme_dir(self, value):
        """Iterate over potential readme for the given directory ``value``."""
        for ext in self.extensions:
            for filename in glob.iglob((value / "*.{}".format(ext)).as_posix()):
                basename = os.path.basename(filename)
                if basename.count(".") == 1:
                    if basename.split(".")[0].lower() == "readme":
                        yield filename

    def iter_readme_file(self, value):
        """Iterate over potential readme for the given file ``value``."""
        for ext in self.extensions:
            for filename in glob.iglob("{}.{}".format(value, ext)):
                yield filename

