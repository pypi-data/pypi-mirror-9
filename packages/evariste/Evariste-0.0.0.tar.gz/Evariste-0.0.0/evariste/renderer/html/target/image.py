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

"""Render images as HTML"""

from evariste.renderer.html.target import HtmlRenderer

IMAGE_EXTENSIONS = [
    "png",
    "jpg",
    "jpeg",
    "gif",
    ]

class HtmlImageRenderer(HtmlRenderer):
    """Render images as HTML"""

    priority = 0
    keyword = "image"

    def match(self, path):
        if not path.report.success:
            return False
        return path.report.target.split('.')[-1].lower() in IMAGE_EXTENSIONS

    def render(self, tree, context):
        """Render ``tree``, which is a :class:`tree.File`, as HTML."""
        return context['render'](
            context,
            tree,
            ["tree_file_image.{}".format(self.extension)],
            )
