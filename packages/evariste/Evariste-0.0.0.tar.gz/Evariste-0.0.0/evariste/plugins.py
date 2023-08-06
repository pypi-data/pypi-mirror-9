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


"""Plugin loader"""

from functools import total_ordering
import importlib
import logging
import os
import pkgutil
import sys

from evariste import errors
import evariste

LOGGER = logging.getLogger(evariste.__name__)

class NoMatch(errors.EvaristeError):
    """No plugin found matching ``value``."""

    def __init__(self, value, available):
        super().__init__()
        self.value = value
        self.available = available

    def __str__(self):
        return "Value '{}' does not match any of {}.".format(
            self.value,
            str(self.available),
            )

class SameKeyword(errors.EvaristeError):
    """Two plugins have the same keyword."""

    def __init__(self, base, keyword, plugin1, plugin2):
        super().__init__()
        self.base = base
        self.keyword = keyword
        self.plugins = (plugin1, plugin2)

    def __str__(self):
        return """Plugins '{}' and '{}' (from '{}') have the same keyword '{}'.""".format(
            self.plugins[0].__name__,
            self.plugins[1].__name__,
            self.base,
            self.keyword,
            )

class NotAPlugin(errors.EvaristeError):
    """Superclass of plugins is not a plugin."""

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def __str__(self):
        return (
            """Class '{obj.__module__}.{obj.__name__}' is not a plugin """
            """(it should inherit from """
            """'{superclass.__module__}.{superclass.__name__}')."""
            ).format(
                obj=self.obj,
                superclass=PluginBase,
            )

class PluginBase:
    """Plugin base: all imported plugins must be subclasses of this class."""
    # pylint: disable=too-few-public-methods
    keyword = None
    description = None
    priority = 0
    default_setup = {}
    plugin_type = []
    subplugin_baseclasses = {}
    subplugins = {}

    def __init__(self, setup):
        self.global_setup = setup
        self._set_default_setup()
        self._load_plugins()

    def _set_default_setup(self):
        """Set default value for this plugin setup, if necessary."""
        for parent in self.__class__.mro(): # pylint: disable=no-member
            if hasattr(parent, "default_setup"):
                self.global_setup.fill_blanks(self.default_setup)

    def _load_plugins(self):
        """Load subplugins."""
        for (keyword, baseclass) in self.subplugin_baseclasses.items():
            self.subplugins[keyword] = PluginLoader(
                self.__module__.split('.')[1:] + [keyword],
                baseclass,
                self.global_setup,
                )

    @property
    def setup(self):
        """Return this plugin setup."""
        return self.global_setup[self.setup_section]

    def match(self, value, *args, **kwargs): # pylint: disable=unused-argument
        """Return ``True`` iff ``value`` is to be compiled by ``self``."""
        raise NotImplementedError()

    @property
    def setup_section(self):
        """Return the name of the section of the object, in the setup file."""
        return ".".join(self.plugin_type + [self.keyword])

@total_ordering
class PluginEntry:
    """Plugin, with associated keyword and priority."""
    # pylint: disable=too-few-public-methods

    def __init__(self, plugin):
        self.plugin = plugin
        self.keyword = plugin.keyword
        self.priority = plugin.priority

    def match(self, value, *args, **kwargs):
        """Call :meth:`self.plugin.match`."""
        return self.plugin.match(value, *args, **kwargs)

    def __eq__(self, other):
        return self.plugin == other.plugin

    def __lt__(self, other):
        priority = self.priority
        if callable(priority):
            priority = priority()
        other_priority = other.priority
        if callable(other_priority):
            other_priority = other_priority()
        if priority == other_priority:
            return self.keyword < other.keyword
        return priority < other_priority

    def __hash__(self):
        return hash(self.plugin)

def expand_path(path):
    """Return ``path`` where environment variables and user directory have been expanded."""
    return os.path.expanduser(os.path.expandvars(path))

class PluginLoader:
    """Plugin loader. Find plugins and select the appropriate one."""

    def __init__(self, base, superclass, setup, libdirs=None):
        """Initialization.

        :param list base: Base module. If ``base == ["foo", "bar"]``, plugins
            are supposed to be submodules of ``evariste.foo.bar``, in
            directory ``evariste/foo/bar``.
        :param type superclass: Base class. Every subclass of ``superclass``
            is a plugin.
        """
        if not issubclass(superclass, PluginBase):
            raise NotAPlugin(superclass)

        self.plugins = set()
        if libdirs is None:
            libdirs = []
        base = ["evariste"] + base

        path = []
        path.extend([
            expand_path(item)
            for item
            in [".evariste", "~/.config/evariste", "~/.evariste"]
            ])
        path.extend([expand_path(item) for item in libdirs])
        path.extend(sys.path)
        evariste_path = [
            os.path.join(item, *base) # pylint: disable=star-args
            for item
            in path
            ]

        for module_finder, name, is_pkg in pkgutil.iter_modules(
                evariste_path,
                prefix=".".join(base) + "."
            ):
            try:
                module = module_finder.find_spec(name).loader.load_module()
            except ImportError:
                continue
            for attr in dir(module):
                if attr.startswith("_"):
                    continue
                obj = getattr(module, attr)

                if (
                        isinstance(obj, type)
                        and
                        issubclass(obj, superclass)
                    ):
                    if obj.keyword is None:
                        continue
                    if obj.keyword in self:
                        if obj != self[obj.keyword].plugin.__class__:
                            raise SameKeyword(
                                "{}.{}".format(
                                    superclass.__module__,
                                    superclass.__name__,
                                    ),
                                obj.keyword,
                                obj,
                                self[obj.keyword].plugin.__class__,
                                )
                    self.plugins.add(PluginEntry(obj(setup)))

    def match(self, value):
        """Return the first plugin matching ``value``.

        A plugin ``Foo`` matches ``value`` if ``Foo.match(value)`` returns
        True.
        """
        for entry in sorted(self, reverse=True):
            if entry.match(value):
                return entry.plugin
        raise NoMatch(value, sorted(self.iter_keywords()))

    def iter_plugins(self):
        """Iterate over plugins (as classes)."""
        for entry in self:
            yield entry.plugin

    def __iter__(self):
        for plugin in self.plugins:
            yield plugin

    def __contains__(self, keyword):
        return keyword in self.iter_keywords()

    def iter_keywords(self):
        """Iterate over plugin keywords."""
        for plugin in self:
            yield plugin.keyword

    def __getitem__(self, keyword):
        for entry in self:
            if entry.keyword == keyword:
                return entry
        raise KeyError(keyword)
