* #1 Quote Évariste Gallois, and find a reliable source.

Version *the sooner the better*
===============================

* #2 Make the strace() call more robust.

Version 0.1.0
=============

* #3 Replace option "plugins" by "enable_plugins" in setup file
* #4 Copyright
  * notice: remove the "1" at the end
  * Use AGPL instead of GPL
* #5 Setup: Path should be relative to setup file. Otherwise, it will fail
* #6 Make a very simple txt renderer
* #7 Compile only if sources and target have changed
  * md5sum changes? rcs last modified change? md5sum for target; rcs for sources?
  * Add a (setup, command line?) option to compile if modification time have changed
* #8 Do not make archive and prune_depends if errors occured
* #9 Write documentation
* #10 Test, test, test!
  * Unittests
  * Code coverage tests?
* #11 Find TODOs

Version 0.2.0
=============

* #13 allow subdirectories of plugins, and make LaTeX plugin a subplugin of command
* #14 I am not sure self.setup works in plugin (a self. setup on a
  renderer.html.readme.FOO plugin brings renderer.html setup)
* #15 Make rcs a real plugin system (right now, one is forced to use git)
* #16 Write a `evsplugins` binary, that can:

  * list paths in which plugins are searched
  * list {readme,renderer,targetrenderer,rcs,actions} plugins
  * dislay plugin name, keyword and priority
  * sort according to path, keyword or priority
  * Examples:

    * ``evsplugins`` List all plugins
    * ``evsplugins ~/.evsconfig`` List all plugins located in directory ~/.evsconfig
    * ``evsplugins --type readme -t target`` List all readme and target plugins.
    * ``evsplugins --type readme,target`` Idem
    * ``evsplugins --type "readme target"`` Idem
    * ``evsplugins --type http.readme -t http.target`` List all readme and target plugins of the html renderer.
    * ``evsplugins --sort type,renderer,priority`` Sort plugins: first sort key is plugin type (renderer, action, etc.); second sort key is rendere (for readme and target plugins; ignored for other types); then sort them by priority. Available sorts are name, priority, keyword, type, renderer. Default is "type,renderer,name".
    * ``evsplugins --show priority,keyword`` Show fields priority and keyword. Available arguments are type, renderer, keyword, priority, name, path. Default is:

      * if one type: ``{renderer}.{keyword} {name} {path}``
      * if several: ``({type}) {renderer}.{keyword} {name} {path}``

    * ``evsplugins --format "({type}) {renderer}.{keyword} {name} {path}"`` More precise output than ``--show``.
* Renderer
    * #17 Write a LaTeX renderer to see how reusable the plugin renderer system is.
    * #18 html log renderer
* #19 Enable multiprocess
* #20 Plugins *This part is inspired by IkiWiki plugin management*
    * Add configurations options *enable_plugins* and *disable_plugins*, to
      enable only a few set of plugins, or enable every plugin but a few ones.
    * Add a metaplugin "goodstuff", enabled by default, enabling some plugins

      * add "renderer.html.goodstuff", enabling default target and readme renderers for html renderer?

    * For renderers: enabling an option (example 2) is not equivalent (is useless) to setting enable_plugins (example 1)

      .. code:: ini

        [setup]
        enable_plugins = renderer.html renderer.html.readme.foo renderer.html.target.bar

      .. code:: ini

        [renderer.html]

        [renderer.html.readme.foo]

        [renderer.html.target.bar]


* Actions
    * #21 Raw: make it configurable (list of regexp to render as raw)
    * #22 LaTeX : make it configurable (binaries to use, custom commands, etc.)
    * #23 Add an `autocmd` action, which associates custom commands to file extensions. Examples:

      .. code:: ini

        [action.autocmd.tex]
        command = pdflatex {basename}
        target = {basename}.pdf

        [action.autocmd.libreoffice]
        extensions = odt ods...
        command = libreoffice --headless --convert-to pdf {filename}
        target = {basename}.pdf

* Templates
    * #24 Load from evariste, /ush/share/evariste, .evariste and ~/.config/evariste
    * #25 Write some not-too-ugly css and js, and use them in the template of the example
* Plugins
    * #26 Add an option *libdirs* to add plugin directories

Version *later*
===============

* TargetRenderer:
    * #27 Image: set image size in configuration files.
    * #28 Make it possible to define in configuration file which TargetRenderer to use.
    * #29 Create a non-default pdf renderer which displays the first page as an image (thumbnail)
* Readme
    * #30 See if one can use images EXIF (or other standard) metadata as readme.
