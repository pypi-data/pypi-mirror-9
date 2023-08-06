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

"""Access to RCS (git, etc.) versionned files."""

import os
import pathlib

from evariste import errors
from evariste.tree import Directory

class NoRepositoryError(errors.EvaristeError):
    """No repository contains the given path."""

    def __init__(self, rcstype, directory):
        super().__init__()
        self.directory = directory
        self.rcstype = rcstype

    def __str__(self):
        return (
            "Could not find any {} repository containing directory '{}'."
            ).format(
                self.rcstype,
                self.directory,
                )

class RCS:
    """Generic class to access to versionned files."""

    def __init__(self, directoryname):
        self.from_source = pathlib.Path(directoryname)

    def tree(self, setup):
        """Return a :class:`Directory` object representing the versionned files.
        """
        tree = Directory(self.from_source, rcs=self, setup=setup)
        for path in self.walk():
            tree.add_subpath(pathlib.Path(path))
        return tree

    def walk(self):
        """Iterate over list of versionned files, descendants of ``self.from_source``.
        """
        raise NotImplementedError()

    def is_versionned(self, path):
        """Return ``True`` iff ``path`` is versionned."""
        raise NotImplementedError()

    @property
    def workdir(self):
        """Return path of the root of the repository."""
        raise NotImplementedError()

    def from_repo(self, path):
        """Return ``path``, relative to the repository root."""
        raise NotImplementedError()

    def last_modified(self, path):
        """Return the datetime of last modification."""
        raise NotImplementedError()
