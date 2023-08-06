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

"""Compilation of {,La,Lua,Xe}TeX files"""

import os

from evariste.action.command import MultiCommand
from evariste import utils

class CompilationEnvironment:
    """Environment of compilation.

    Stores some variables related to the compilation of one LaTeX file.
    """
    # pylint: disable=too-few-public-methods

    BIN = {
        'latex': 'latex',
        'bibtex': 'bibtex',
        # INDEX
        }

    def __init__(self, path):
        self.bin = self.BIN.copy()
        self.path = path
        self.latex_todo = 1

class Latex(MultiCommand):
    """Compilation of *TeX files."""

    # TODO add index generation (look for INDEX in this file)

    keyword = "latex"
    priority = 100

    DEFAULT_COMMANDS = [
        "latex",
        "?bibtex",
        # INDEX
        "?latex",
        ]
    PREDEFINED_COMMANDS = {
        'latex': '{latex} {basename}',
        'pdflatex': 'pdflatex {basename}',
        'lualatex': 'lualatex {basename}',
        'xelatex': 'xelatex {basename}',
        'bibtex': '{bibtex} {basename}',
        'biblatex': 'biblatex {basename}',
        # INDEX
        }
    TARGET = {
        'latex': '{basename}.dvi',
        'pdflatex': '{basename}.pdf',
        'lualatex': '{basename}.TODO', # TODO
        'xelatex': '{basename}.TODO', # TODO
        }
    CONDITIONAL_COMMANDS = [
        'latex',
        'bibtex',
        # INDEX
        ]

    def match(self, value):
        return value.suffix == ".tex"

    def _compile(self, path):
        # pylint: disable=arguments-differ
        return super()._compile(path, CompilationEnvironment(path))

    def _read_config(self, path, env):
        # pylint: disable=signature-differs
        # Reading commands
        precommands = []
        postcommands = []
        commands = []
        if self.setup_section in env.path.config:
            for option in env.path.config[self.setup_section]:
                if option.startswith("pre"):
                    precommands.append("!{}".format(env.path.config[self.setup_section][option]))
                elif option.startswith("cmd"):
                    commands.append(env.path.config[self.setup_section][option])
                elif option.startswith("post"):
                    postcommands.append("!{}".format(env.path.config[self.setup_section][option]))
        if not commands:
            commands = self.DEFAULT_COMMANDS
        self._commands = precommands + commands + postcommands

        # Reading binaries
        for key in env.bin:
            if env.path.config.has_option(self.setup_section, key):
                if env.path.config.get(self.setup_section, key) is not None:
                    env.bin[key] = env.path.config.get(self.setup_section, key)

        # Setting target
        if not env.path.config.has_option(self.setup_section, 'target'):
            basetarget = env.path.format(self.TARGET[env.bin['latex']])
        else:
            basetarget = env.path.format(env.path.config[self.setup_section]["target"])
        self._report.target = os.path.join(
            env.path.parent.from_source.as_posix(),
            basetarget,
            )

    def _format_command(self, command, env):
        """Iterate over commands that are to be executed."""
        if command.startswith("?") and command[1:] in self.CONDITIONAL_COMMANDS:
            yield from getattr(self, "_conditionnal_command_{}".format(command[1:]))(env)
        elif command.startswith("!"):
            yield utils.partial_format(command[1:], **env.bin)
        elif command in self.PREDEFINED_COMMANDS:
            yield utils.partial_format(self.PREDEFINED_COMMANDS[command], **env.bin)
        else:
            yield utils.partial_format(command, **env.bin)

    def iter_commands(self, env):
        for command in self._commands:
            yield from self._format_command(command, env)

    def _conditionnal_command_bibtex(self, env):
        """Yield a bibtex command, if necessary.

        "Necessary" means that option 'bibtex' appears in configuration file.

        It might be detected, some day, by looking at the LaTeX log.
        """
        if env.path.config.has_option(self.setup_section, 'bibtex'):
            env.latex_todo += 1
            yield from self._format_command('bibtex', env)

    def _conditionnal_command_latex(self, env):
        """Yield as many `latex` commands as necessary.

        Previous commands may have incremented `env.latex_todo`.
        """
        while env.latex_todo != 0:
            env.latex_todo -= 1
            yield from self._format_command('latex', env)
