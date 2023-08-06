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

"""Actions performed to compile files."""

import logging

from evariste import plugins, errors

LOGGER = logging.getLogger(__name__)

################################################################################
# Actions

class Action(plugins.PluginBase):
    """Generic action"""
    # pylint: disable=too-many-instance-attributes, too-few-public-methods

    plugin_type = ["action"]

    def __init__(self, setup):
        super().__init__(setup)

    def _compile(self, path):
        """Perform compilation."""
        raise NotImplementedError()

    def compile(self, path):
        """Compile ``path``, catching :class:`EvaristeError` exceptions.
        """
        try:
            return self._compile(path)
        except errors.EvaristeError as error:
            LOGGER.log(15, str(error))
            return Report(
                path,
                success=False,
                error=str(error),
                log=[LogInternal(str(error))],
                )

class DirectoryAction(Action):
    """Fake action on directories."""
    # pylint: disable=abstract-method, too-few-public-methods

    def match(self, dummy):
        return False

    def _compile(self, path):
        return Report(
            path,
            success=self.success(path),
            error="At least one file in this directory failed.",
            target=None,
            )

    @staticmethod
    def success(path):
        """Return ``True`` if compilation of all subpath succeeded."""
        for sub in path:
            if not path[sub].report.success:
                return False
        return True

def load_actions(setup):
    """Return the :class:`PluginLoader`` of action plugins."""
    return plugins.PluginLoader(["action"], Action, setup)

################################################################################
# Reports

class Report:
    """Report of an action. Mainly a namespace with very few methods."""

    def __init__(
            self,
            path,
            target=None,
            error="Undocumented error",
            success=False,
            log=None,
            depends=None,
        ):
        # pylint: disable=too-many-arguments

        self.depends = depends
        if self.depends is None:
            self.depends = set()

        self.log = log
        if self.log is None:
            self.log = []

        self.path = path
        self.target = target
        self._success = success
        self.error = error

    @property
    def full_depends(self):
        """List of files this action depends on, including ``self.path``."""
        return self.depends | set([self.path.from_cwd])

    @property
    def success(self):
        """Success getter"""
        return self._success

    @success.setter
    def success(self, value):
        """Success setter."""
        self._success = value




################################################################################
# Exceptions

class MissingOption(errors.EvaristeError):
    """No command was provided for action :class:`Command`."""

    def __init__(self, filename, section, option):
        super().__init__()
        self.filename = filename
        self.section = section
        self.option = option

    def __str__(self):
        return (
            "Configuration for file '{file}' is missing option '{option}' in section '{section}'."
            ).format(
                file=self.filename,
                section=self.section,
                option=self.option,
            )

################################################################################
# Log

class Log:
    """Action log"""
    # pylint: disable=too-few-public-methods

    def __init__(self, identifier, content):
        self.identifier = identifier
        self.content = content

    def __str__(self):
        return "({}) {}".format(self.identifier, self.content)

class LogInternal(Log):
    """Log of internal exception"""
    # pylint: disable=too-few-public-methods

    def __init__(self, content):
        super().__init__("Internal error", content)

class LogFile(Log):
    """Log from file"""
    # pylint: disable=too-few-public-methods

    def __init__(self, filename):
        with open(filename) as file:
            super().__init__(filename, file.read())

class LogPipe(Log):
    """Log from pipe"""
    # pylint: disable=too-few-public-methods

    IDENTIFIERS = {
        0: "standard input", # Why would one do that?
        1: "standard output",
        2: "standard error",
        }

    def __init__(self, pipe, content=""):
        super().__init__(self.IDENTIFIERS.get(pipe, str(pipe)), content)

    def read(self, pipe):
        """Read content from pipe."""
        while 1:
            line = pipe.readline()
            if line == '':
                break
            self.content += line
            LOGGER.debug("({}) {}".format(self.identifier, line.strip()))

class MultiLog(Log):
    """List of logs"""
    # pylint: disable=too-few-public-methods

    def __init__(self, sublogs):
        super().__init__("multilog", "")
        self._sublogs = sublogs

    def __iter__(self):
        yield from self._sublogs

