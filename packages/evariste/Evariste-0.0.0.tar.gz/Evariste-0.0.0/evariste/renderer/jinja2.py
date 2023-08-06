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

"""Abstract class for jinja2 renderers."""

import jinja2
import os
import pkg_resources
import pathlib
import textwrap

from evariste import utils
from evariste.renderer.dest import DestRenderer
from evariste.target.jinja2 import JinjaRenderer as TargetJinjaRenderer
from evariste.readme.jinja2 import JinjaRenderer as ReadmeJinjaRenderer

class JinjaRenderer(DestRenderer):
    """Abstract class for jinja2 renderers."""
    # pylint: disable=too-few-public-methods

    extension = None
    subplugin_baseclasses = {
        "target": TargetJinjaRenderer,
        "readme": ReadmeJinjaRenderer,
        }

    def __init__(self, setup):
        super().__init__(setup)

        self.environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.dirname(pkg_resources.resource_filename( #pylint: disable=no-member
                    self.__class__.__module__,
                    os.path.join("data", "templates", "tree.{}".format(self.extension))
                ))
            )
        )
        self.environment.filters['basename'] = os.path.basename


    def render(self, tree):
        return self._render(
            tree=tree,
            template="tree.{}".format(self.extension),
            context={
                'destdir': pathlib.Path(self.destdir),
                'setup': self.setup,
                'global_setup': self.global_setup,
                'render': self._render,
                'render_download': self._render_download,
                'render_readme': self._render_readme,
                'render_file': self._render_file,
                'render_directory': self._render_directory,
                'render_template': self._render_template,
                },
            )

    @jinja2.contextfunction
    def _render(self, context, tree, template):
        """Render the tree, using given template (or template list)."""
        if isinstance(context, dict):
            context['tree'] = tree
        else:
            context.vars['tree'] = tree
        if tree.is_file() and tree.report.success:
            utils.copy(
                os.path.join(
                    tree.root.from_cwd.as_posix(),
                    tree.report.target,
                    ),
                os.path.join(
                    context['destdir'].as_posix(),
                    tree.report.target,
                    )
                )
        return textwrap.indent(
            self.environment.get_or_select_template(template).render(context),
            "  ",
            )

    @jinja2.contextfunction
    def _render_directory(self, context, tree):
        """Render ``tree``, which is a :class:`tree.Directory`, as HTML."""
        return self._render(context, tree, "tree_directory.{}".format(self.extension))

    @jinja2.contextfunction
    def _render_file(self, context, tree):
        """Render ``tree``, which is a :class:`tree.File`."""
        return self.subplugins["target"].match(tree).render(tree, context)

    @jinja2.contextfunction
    def _render_download(self, context, tree):
        """Render the code downloading the archive."""
        path = tree.make_archive(context["destdir"])
        context.vars['href'] = path.as_posix()
        context.vars['content'] = path.name
        return self.environment.get_template("download.{}".format(self.extension)).render(context) # pylint: disable=no-member

    @jinja2.contextfunction
    def _render_readme(self, context, tree):
        """Find the readme of tree, and returns the corresponding code."""
        # pylint: disable=unused-argument
        return tree.render_readme(self.subplugins["readme"], context)

    @jinja2.contextfunction
    def _render_template(self, context, template):
        """Render template given in argument."""
        with open(template) as file:
            return self.environment.from_string(file.read()).render(context)
