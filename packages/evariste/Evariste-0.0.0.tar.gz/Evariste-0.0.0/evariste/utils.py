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

"""A rag-bag of utility functions that did not fit anywhere else."""

import os
import shutil

def copy(source, destination):
    """Copy ``source`` to ``destination``, creating directories if necessary."""
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.copy(source, destination)

### Partial format
### TODO There must be a cleaner way to do this. I have no Internet right now
def partial_format(string, *args, **kwargs):
    """Format string, leaving unfilled fields untouched.

    >>> partial_format("To {verb} or {negation} to {verb}", negation="not")
    "To {verb} or not to {verb}"
    """

    def fields(string):
        """Iterator over the fields of the string.

        >>> list(fields("To {be} or {not} to be"))
        ["be", "not"]
        """
        store = False
        current = ""
        for char in string:
            if char == '{':
                store = True
            elif char == '}':
                store = False
                yield current
                current = ""
            else:
                if store:
                    current += char

    dictionary = {}
    for field in fields(string):
        dictionary[field] = '{' + field + '}'

    dictionary.update(kwargs)
    return string.format(*args, **dictionary) # pylint: disable=star-args
