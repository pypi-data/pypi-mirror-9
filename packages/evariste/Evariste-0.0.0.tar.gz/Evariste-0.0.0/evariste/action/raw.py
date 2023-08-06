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

"""Raw action: does nothing; simply provides a link to download file."""

from evariste import action


class Raw(action.Action):
    """Raw action"""
    # pylint: disable=too-few-public-methods

    keyword = "raw"
    priority = -100

    # TODO complete:
    # - archives
    # - libreoffice / Ms Office
    # See if it is not better with mimetypes.
    MATCH_SUFFIXES = [
        ".pdf", ".dvi",
        ".png", ".jpg", ".jpeg", ".gif",
        ]

    def _compile(self, path):
        return action.Report(
            path,
            target=path.from_source.as_posix(),
            success=True,
            )

    def match(self, value):
        return value.suffix in self.MATCH_SUFFIXES
