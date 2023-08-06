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

"""Access to git-versionned files."""

from datetime import datetime
import itertools
import os
import pygit2

from evariste import rcs

RCS_TYPE = 'git'

class Git(rcs.RCS):
    """Access git-versionned files"""
    # pylint: disable=no-member

    def __init__(self, directoryname):
        super().__init__(directoryname)
        try:
            self.repository = pygit2.Repository(
                pygit2.discover_repository(
                    directoryname
                    )
                )
        except KeyError:
            raise rcs.NoRepositoryError(RCS_TYPE, directoryname)

    def walk(self):
        root = self.from_source.resolve().relative_to(self.workdir)
        for entry in self.repository.index:
            if entry.path.startswith(root.as_posix()):
                yield os.path.relpath(entry.path, root.as_posix())

    def is_versionned(self, path):
        from_repo = self.from_repo(path)
        for entry in self.repository.index:
            if from_repo == entry.path:
                return True
        return False

    @property
    def workdir(self):
        return self.repository.workdir

    def from_repo(self, path):
        return os.path.relpath(
            path.resolve().as_posix(),
            self.workdir
            )

    def _walk_for_files(self, path):
        """TODO

        Copied and adapted from
        https://github.com/libgit2/pygit2/issues/200#issuecomment-15899713
        """
        walker = self.repository.walk(
            self.repository.head.target,
            pygit2.GIT_SORT_TIME,
            )
        commit0 = next(walker)
        for commit1 in walker:
            files_in_diff = (
                (x.old_file_path, x.new_file_path)
                for x in commit1.tree.diff_to_tree(commit0.tree)
                )
            if path in itertools.chain(*files_in_diff): # pylint: disable=star-args
                return commit0
            commit0 = commit1

    def last_modified(self, path):
        return datetime.fromtimestamp(self._walk_for_files(self.from_repo(path)).commit_time)

