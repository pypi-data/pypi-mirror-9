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

"""Render report as an HTML (body) page."""

import textwrap

import evariste

class HTMLLogRenderer(evariste.renderer.Renderer):
    """Render logs as an HTML (body) page."""

    keyword = "htmllog"
    description = textwrap.dedent(
        "Render the compilation report as a single html page (body only)."
        )
