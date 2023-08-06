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

"""Directory representation and compilation."""

import configparser
import functools
import logging
import os
import pathlib
import tarfile

from evariste import action, plugins, utils

LOGGER = logging.getLogger(__name__)

@functools.total_ordering
class Tree:
    """Directory tree"""
    # pylint: disable=too-many-instance-attributes

    def __init__(self, path, parent=None, rcs=None, setup=None):
        self._subpath = {}
        self.report = None
        self.ignored = []
        self._config_files = []
        self.path = pathlib.Path(path)
        self.parent = parent
        self.config = None
        if parent is None:
            self.from_cwd = self.path
            self.from_source = pathlib.Path(".")
        else:
            self.from_cwd = parent.from_cwd / self.path
            self.from_source = parent.from_source / self.path
        if rcs is None:
            self.rcs = self.parent.rcs
        else:
            self.rcs = rcs
        if setup is None:
            self.setup = self.parent.setup
        else:
            self.setup = setup
        self._set_ignore()
        self._gather_config_files()

    def is_root(self):
        """Return ``True`` iff ``self`` is the root."""
        return self.parent is None

    @property
    def root(self):
        """Return the root of the tree."""
        if self.is_root():
            return self
        return self.parent.root

    def add_subpath(self, sub):
        """Add a subpath"""
        if len(sub.parts) > 1:
            self[sub.parts[0]].add_subpath(pathlib.Path(*sub.parts[1:]))
        else:
            self[sub.parts[0]] # pylint: disable=pointless-statement

    def __iter__(self):
        return iter(self._subpath)

    def keys(self):
        """Iterator over subpaths (as :class:`str` objects)."""
        yield from self._subpath.keys()

    def values(self):
        """Iterator over subpaths (as :class:`Tree` objects)."""
        yield from self._subpath.values()

    def __contains__(self, key):
        return key in self._subpath

    def __getitem__(self, key):
        if key not in self:
            if (self.from_cwd / key).is_dir():
                path_type = Directory
            else:
                path_type = File
            self._subpath[key] = path_type(key, parent=self)
        return self._subpath[key]

    def __delitem__(self, item):
        if item in self:
            del self._subpath[item]
            if len(self._subpath) == 0 and self.is_dir() and self.parent is not None:
                del self.parent[self.path.name]


    def __str__(self):
        return self.from_cwd.as_posix()

    def __len__(self):
        return len(self._subpath)

    def __eq__(self, other):
        return self.from_source == other.from_source

    def __lt__(self, other):
        return self.from_source < other.from_source

    def pprint(self, prefix="", last=True, print_function=print):
        """Pretty print of tree."""
        line = ""
        line += prefix
        if last:
            line += "└"
        else:
            line += "├"
        line += "─"
        if self.is_dir():
            line += "┬"
        else:
            line += "─"
        line += "╼ " + str(self.path)
        if last:
            postfix = "  "
        else:
            postfix = "│ "
        print_function(line)
        counter = 0
        for sub in sorted(self):
            counter += 1
            self[sub].pprint(
                prefix=prefix + postfix,
                last=(counter == len(self)),
                print_function=print_function
                )

    def is_dir(self):
        """Return `True` iff `self` is a directory."""
        return issubclass(self.__class__, Directory)

    def is_file(self):
        """Return `True` iff `self` is a file."""
        return issubclass(self.__class__, File)

    def walk(self, dirs=False, files=True):
        """Iterator over files or directories  of `self`.

        :param bool dirs: If `False`, do not yield directories.
        :param bool files: If `False`, do not yield files.
        """
        if (
                (dirs and self.is_dir())
                or
                (files and self.is_file())
            ):
            yield self
        for sub in sorted(self):
            yield from self[sub].walk(dirs, files)

    def prune_ignored(self):
        """Remove ignored paths from the tree."""
        # Recursive call
        for sub in self:
            self[sub].prune_ignored()

        # Process ``self``
        for regexp in self.ignored:
            for file in self.from_cwd.glob(regexp):
                self.root.prune(file.relative_to(self.root.from_cwd))

    def prune(self, path):
        """Remove a file.

        Argument can be either a :class:`pathlib.Path` or a :class:`tuple`.
        """
        if isinstance(path, tuple):
            parts = path
        elif isinstance(path, pathlib.Path):
            parts = path.parts
        else:
            raise ValueError
        if len(parts) == 1:
            del self[parts[0]]
        else:
            self[parts[0]].prune(parts[1:])

    @property
    def config_files(self):
        """Iterate over the names of configuration files affecting ``self``.

        This includes the configuration files of parent directories."""
        if self.parent is not None:
            yield from self.parent.config_files
        yield from self._config_files

    def set_config(self):
        """Set the configuration of current directory."""
        # Recursive call
        for sub in self:
            self[sub].set_config()

        # Set configuration of `self`
        self.config = configparser.ConfigParser(allow_no_value=True)
        for filename in self.config_files:
            with open(filename) as file:
                self.config.read_file(file)

    def _set_ignore(self):
        """Set the list of ignored regular expressions."""
        raise NotImplementedError()

    def _gather_config_files(self):
        """Iterator over the names of configuration files specific to ``self``
        """
        raise NotImplementedError()

    def compile_root(self, compilers):
        """Recursively compile files. This method is to be called by the root."""
        if not self.is_root():
            raise RuntimeError("Method 'compile_root()' can only be called on root of tree.")

        ## Attempt to multiprocess. Does not work because data is not shared.
        ## TODO: Implement multiprocess
        #pool = multiprocessing.pool.Pool()
        #self.compile(compilers, pool)
        #pool.close()
        #pool.join()
        self.compile(compilers)
        self.prune_depends()

    def compile(self, compilers, pool=None):
        """Recursively compile files."""
        raise NotImplementedError()

    def prune_depends(self):
        """Delete files that are dependencies of others."""
        raise NotImplementedError()

    def format(self, string):
        """Format given string, with several variables related to ``self.path``.
        """
        suffix = self.path.suffix
        if suffix.startswith("."):
            suffix = suffix[1:]
        return string.format(
            dirname=self.parent.from_cwd.as_posix(),
            filename=self.path.name,
            fullname=self.from_cwd.as_posix(),
            extension=suffix,
            basename=self.path.stem,
            )

    def render_readme(self, renderers, *args, **kwargs):
        """Find and render the readme corresponding to ``self``.

        If no readme was found, return an empty string.
        """
        for renderer in renderers.iter_plugins():
            for filename in renderer.iter_readme(
                    self.from_cwd,
                    directory=isinstance(self, Directory),
                ):
                return renderer.render(filename, *args, **kwargs)
        return ""

    def full_depends(self):
        """Return the list of all dependencies of this tree (recursively)."""
        raise NotImplementedError()


class Directory(Tree):
    """Directory"""

    def _set_ignore(self):
        """Set the list of ignored regular expressions."""
        ignorename = os.path.join(self.from_cwd.as_posix(), ".evsignore")
        if os.path.exists(ignorename):
            with open(ignorename) as file:
                self.ignored.extend([line.strip() for line in file.readlines()])

    def _gather_config_files(self):
        """Iterator over the names of configuration files specific to ``self``
        """
        name = os.path.join(self.from_cwd.as_posix(), ".evsconfig")
        if os.path.exists(name):
            self._config_files.append(name)

    def compile(self, compilers, pool=None):
        """Recursively compile files."""
        for sub in sorted(self):
            self[sub].compile(compilers, pool)
        self.report = action.DirectoryAction(self.setup).compile(self)

    def prune_depends(self):
        """Delete files that are dependencies of others."""
        # We cannot use `for sub in self:` here because dictionnary
        # `self._subpath` may change during iteration.
        for sub in list(self._subpath.keys()):
            if sub in self:
                self[sub].prune_depends()

    def full_depends(self):
        for sub in self:
            yield from self[sub].full_depends()


class File(Tree):
    """File"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report = None

    def _set_ignore(self):
        """Set the list of ignored regular expressions."""
        for name in ["{}.ignore", ".{}.ignore"]:
            if os.path.exists(os.path.join(
                    self.parent.from_cwd.as_posix(),
                    name.format(self.path),
                )):
                self.parent.ignored.append(self.path.name)

    def _gather_config_files(self):
        """Set the configuration of current file."""
        for name in [".{}.evsconfig", "{}.evsconfig"]:
            name = os.path.join(
                self.parent.from_cwd.as_posix(),
                name.format(self.path),
                )
            if os.path.exists(name):
                self._config_files.append(name)

    def _compile(self, compile_function):
        """Actual compilation."""
        LOGGER.info("Compiling '{}'…".format(self.from_cwd))
        self.report = compile_function(self)
        if self.report.success:
            LOGGER.info("Compiling '{}': success.".format(self.from_cwd))
        else:
            LOGGER.info("Compiling '{}': failed.".format(self.from_cwd))

    def compile(self, compilers, pool=None):
        """Compile file, using multitasking poll if available."""
        try:
            if self.config.has_option('action', 'plugin'):
                compiler = compilers[self.config['action']['plugin']].plugin
            else:
                compiler = compilers.match(self.from_cwd)
        except plugins.NoMatch:
            del self.parent[self.path.name]
            return None

        if pool is None:
            self._compile(compiler.compile)
        else:
            pool.apply_async(self._compile, compiler.compile)


    def prune_depends(self):
        """Remove dependencies from tree."""
        if self.report:
            for path in self.report.depends:
                self.root.prune(
                    path.resolve().relative_to(
                        self.root.from_cwd.resolve()
                        )
                    )

    def make_archive(self, destdir):
        """Make an archive of ``self`` and its dependency.

        Stes are:
        - build the archive;
        - copy it to ``destdir``;
        - return the path of the archive, relative to ``destdir``.

        If ``self`` has no dependencies, consider the file as an archive.
        """
        if len(self.report.full_depends) == 1:
            utils.copy(self.from_cwd.as_posix(), (destdir / self.from_source).as_posix())
            return self.from_source
        else:
            archivepath = self.from_source.with_suffix(
                "{}.{}".format(self.from_source.suffix, 'tar.gz')
                )
            os.makedirs(os.path.dirname((destdir / archivepath).as_posix()), exist_ok=True)
            with tarfile.open(
                (destdir / archivepath).as_posix(),
                mode='w:gz',
                ) as archive:
                for file in self.report.full_depends:
                    archive.add(
                        file.as_posix(),
                        file.relative_to(self.parent.from_cwd).as_posix(),
                        )
            return archivepath

    def last_modified(self):
        """Return the last modified date and time of ``self``."""
        return self.rcs.last_modified(self.from_cwd)

    def full_depends(self):
        yield from self.report.full_depends


def build_tree(repository, setup):
    """Return a directory, fully set."""
    directory = repository.tree(setup)
    directory.set_config()
    directory.prune_ignored()
    return directory
