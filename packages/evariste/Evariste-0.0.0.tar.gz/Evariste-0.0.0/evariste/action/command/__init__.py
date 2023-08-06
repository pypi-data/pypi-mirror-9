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

"""Shell command: perform a (list of) shell command(s) on files."""

import logging
import os
import pathlib
import re
import subprocess
import threading

import evariste
from evariste import action

LOGGER = logging.getLogger(evariste.__name__)
STRACE_RE = re.compile(r'^open\("(?P<name>.*)",.*O_RDONLY.*\) = *[^ -].*')

def system(command, path, logreaders, depends):
    """Run a system command.

    This function:
    - run command;
    - log standard output and error;
    - track opened files.
    """

    def _process_strace_line(line):
        """Process output line of strace, and complete ``depends`` if relevant."""
        match = STRACE_RE.match(line)
        if match:
            try:
                name = pathlib.Path(
                    match.groupdict()["name"]
                    ).relative_to(
                        path.root.from_source
                    )
            except ValueError:
                return
            if name != path.path:
                if path.rcs.is_versionned(path.parent.from_cwd / name):
                    depends.add(path.parent.from_cwd / name)

    def _process_strace(pipe):
        """Process strace output, to find dependencies."""
        current = ""
        while 1:
            line = os.read(pipe, 1)
            if line == b'':
                break
            elif line == b'\n':
                _process_strace_line(current)
                current = ""
            else:
                current += line.decode()
        _process_strace_line(current)

    out3, in3 = os.pipe()
    process = subprocess.Popen(
        r"""strace -o "! sh -c 'cat >&{fd}'" -e trace=open {command}""".format(
            fd=in3,
            command=command,
            ),
        shell=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        pass_fds=(in3, out3),
        universal_newlines=True,
        cwd=path.parent.from_cwd.as_posix(),
        )

    threads = [
        threading.Thread(
            target=function,
            daemon=True,
            kwargs={
                'pipe' : pipe,
                }
            )
        for (function, pipe) in [
            (_process_strace, out3),
            (logreaders[0], process.stdout),
            (logreaders[1], process.stderr),
            ]
        ]
    for thread in threads:
        thread.start()
    process.wait()
    os.close(in3)
    for thread in threads:
        thread.join()
    os.close(out3)

    return process.returncode

class Command(action.Action):
    """Shell command action."""
    # pylint: disable=too-few-public-methods

    keyword = "command"

    def match(self, value): # pylint: disable=unused-argument
        """Return ``True`` iff ``value`` is to be compiled by ``self``."""
        return False

    def _compile(self, path):
        if not path.config.has_option(self.setup_section, 'command'):
            raise evariste.action.MissingOption(path.from_cwd, self.setup_section, 'command')
        command = path.format(path.config[self.setup_section]["command"])

        if not path.config.has_option(self.setup_section, 'target'):
            raise evariste.action.MissingOption(path.from_cwd, self.setup_section, 'target')

        LOGGER.log(15, "Runnig command: {}".format(command))

        pipes = [
            action.LogPipe(1),
            action.LogPipe(2),
            ]

        depends = set()
        returncode = system(
            command=command,
            path=path,
            logreaders=[pipe.read for pipe in pipes],
            depends=depends,
            )

        return action.Report(
            path,
            log=pipes,
            success=(returncode == 0),
            error="Command '{}' failed.".format(command),
            target=os.path.join(
                path.parent.from_source.as_posix(),
                path.format(path.config[self.setup_section]["target"])
                ),
            depends=depends,
            )

class MultiCommand(action.Action):
    """Chain of commands"""

    keyword = "multicommand"

    def __init__(self, setup):
        super().__init__(setup)
        self._commands = []
        self._report = None # Temporary report. It will be completed during compilation.

    def match(self, value):
        return False

    def iter_commands(self, env):
        """Iterator over the list of commands.

        :param object env: TODO
        """
        # pylint: disable=unused-argument
        yield from self._commands

    def run_subcommand(self, command):
        """Run a subcommand TODO"""
        LOGGER.log(15, "Runnig command: {}".format(command))
        pipes = [
            action.LogPipe(1),
            action.LogPipe(2),
            ]
        self._report.log.append(action.MultiLog(pipes))
        return 0 == system(
            command=command,
            path=self._report.path,
            logreaders=[log.read for log in pipes],
            depends=self._report.depends,
            )

    def _read_config(self, path, env=None):
        """Read and parse list of commands from configuration file.

        :param object env: TODO
        """
        # pylint: disable=unused-argument
        self._commands = []
        for option in path.config.options(self.setup_section):
            if option.startswith("cmd"):
                self._commands.append(
                    path.format(
                        path.config.get(self.setup_section, option)
                        )
                    )
        if not self._commands:
            raise action.MissingOption(path.from_cwd, self.setup_section, 'cmd*')
        if not path.config.has_option(self.setup_section, 'target'):
            raise action.MissingOption(path.from_cwd, self.setup_section, 'target')
        self._report.target = os.path.join(
            path.parent.from_source.as_posix(),
            path.format(path.config[self.setup_section]["target"])
            )


    def _compile(self, path, env=None):
        """TODO

        :param object env: TODO
        """
        # pylint: disable=arguments-differ
        self._report = action.Report(
            path,
            success=True,
            )
        self._read_config(path, env)
        for command in self.iter_commands(env):
            parsed_command = path.format(command)
            if not self.run_subcommand(parsed_command):
                self._report.success = False
                self._report.error = "Command '{}' failed.".format(parsed_command)
                break
        return self._report
