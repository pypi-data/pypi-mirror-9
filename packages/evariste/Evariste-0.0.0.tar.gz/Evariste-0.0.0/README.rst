Évariste — Recursively compile and publish a dircetory tree
===========================================================

|sources| |pypi| |documentation| |license|

.. note::

  As of 20/03/2015, this project is under active development, and is not usable
  yet.

Examples
--------

TODO Give links to the ikiwiki plugin and my website.

Stability
---------

Evariste is to be considered instable at least until version `0.2.0
</spalax/evariste/milestones/2>`_.

I tried to make Evariste extendable throught plugins, but right now I only
wrote one plugin, whereas version `0.2.0 road map
</spalax/evariste/milestones/2>`_ includes writing some other ones.  Thus,
version `0.2.0 </spalax/evariste/milestones/2>`_ can be seen as a way to test
the plugin system, find many bugs, rewrite parts of it, and deliver a (little
more) mature version of it.

Thus, things *will* change with version `0.2.0
</spalax/evariste/milestones/2>`_.

If you do want to write something using Evariste API (a plugin, for instance),
you can get in touch with me beforehand to discuss it, to prevent you from
writing code that will simply not work with version `0.2.0
</spalax/evariste/milestones/2>`_.

Download and install
--------------------

* From sources:

  * Download: https://pypi.python.org/pypi/evariste
  * Install (in a `virtualenv`, if you do not want to mess with your distribution installation system)::

        python3 setup.py install

..

    * From pip::

        pip install evariste

Documentation
-------------

* The compiled documentation is available on `readthedocs
  <http://evariste.readthedocs.org>`_

* To compile it from source, download and run::

      cd doc && make html


.. |documentation| image:: http://readthedocs.org/projects/evariste/badge
  :target: http://evariste.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/evariste.svg
  :target: http://pypi.python.org/pypi/evariste
.. |license| image:: https://img.shields.io/pypi/l/evariste.svg
  :target: http://www.gnu.org/licenses/gpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/sources-evariste-brightgreen.svg
  :target: http://git.framasoft.org/spalax/evariste
