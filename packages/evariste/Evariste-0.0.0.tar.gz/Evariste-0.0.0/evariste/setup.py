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

"""TODO Parse setup file."""

import collections
import configparser

_DEFAULT_SETUP = {
    'setup': {
        'source': '.',
        },
    'renderer': {
        'plugins': '',
        },
    }

def Options(*args, **kwargs):
    """Return a :class:`collections.defaultdict` object, default being `None`.
    """
    # pylint: disable=invalid-name
    return collections.defaultdict(lambda: None, *args, **kwargs)

def Sections(*args, **kwargs):
    """Return a :class:`collections.defaultdict` object, default being `Options`
    """
    # pylint: disable=invalid-name
    return collections.defaultdict(Options, *args, **kwargs)

class Setup:
    """Representation ef Evariste setup."""

    def __init__(self, dictionary=None):
        if dictionary is None:
            dictionary = {}
        self.dict = Sections()
        self.fill_blanks(dictionary)
        self.fill_blanks(_DEFAULT_SETUP)

        for section in ["renderer", "action"]:
            if "plugins" in self[section]:
                self[section]["plugins"] = self[section]["plugins"].strip().split()

    def __iter__(self):
        yield from self.dict

    def __getitem__(self, value):
        return self.dict[value]

    def __str__(self):
        return "{{{}}}".format(", ".join([
            "{}: {}".format(key, value)
            for key, value
            in self.dict.items()
            ]))

    def fill_blanks(self, dictionary):
        """Fill unset self options with argument."""
        for section in dictionary:
            if section in self.dict:
                for option in dictionary[section]:
                    if option not in self.dict[section]:
                        self.dict[section][option] = dictionary[section][option]
            else:
                self.dict[section] = Options(dictionary[section])

    @classmethod
    def from_file(cls, filename):
        """Parse configuration file ``filename``."""
        with open(filename) as file:
            return cls.from_string(file.read())

    @classmethod
    def from_string(cls, string):
        """Parse ``string`` as the content of a configuration file."""
        config = configparser.ConfigParser(allow_no_value=True)
        config.read_string(string)
        return cls.from_config(config)

    @classmethod
    def from_config(cls, setup):
        """Parse ``setup`` as a :class:`configparser.ConfigParser` object."""
        dictionary = dict()
        for section in setup:
            if section == "DEFAULT":
                continue
            dictionary[section] = dict()
            for option in setup[section]:
                dictionary[section][option] = setup[section][option]
        return cls(dictionary)
