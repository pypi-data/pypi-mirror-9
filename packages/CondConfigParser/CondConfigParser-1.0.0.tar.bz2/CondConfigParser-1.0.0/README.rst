===============================================================================
CondConfigParser
===============================================================================
Python library for parsing configuration files with conditionals
-------------------------------------------------------------------------------

CondConfigParser is a Python library designed to help Python application
developers to parse configuration files. Compared to well-known modules
such as `configparser`_ and `json`_, the main specificity of
CondConfigParser is that it allows the end user to define conditions
using boolean operators and specific sections in the configuration file
that are only applied when the corresponding condition is fulfilled.

.. _configparser: https://docs.python.org/3/library/configparser.html#module-configparser
.. _json: https://docs.python.org/3/library/json.html#module-json

The configuration file format allows the end user to define variables of
type boolean, string or list. These variables, in addition to *external
variables* defined by the application, can be combined with Python-like
syntax to define the conditions (called *predicates*) mentioned in the
previous paragraph.

Lists in CondConfigParser may be nested at will. Variable definitions
may refer to previously-defined variables. Predicates can combine
``==``, ``!=`` and ``in`` tests using as many logical ``or``, ``and``,
``not`` operators and parentheses as necessary. Such “logical
expressiveness” (and much more) could be obtained by reading
configuration files interpreted as Python code, however:

  - the syntax in such a case would not allow the almost-freeform
    options that are permitted by CondConfigParser (where the
    application chooses how to interpret the “options”);

  - when an application interprets user configuration files as Python
    code, it exposes its users to some risk in case a malicious user
    manages to sneak code of his choice into a configuration file of the
    victim (think about configuration file snippets copied from Internet
    forums...).

Regarding the second point in particular, CondConfigParser never uses
``eval`` or ``exec`` to parse configuration files. It should thus be
safe to work with any configuration file, including files prepared by
malicious users.

.. _end-of-intro:

Home page
---------

CondConfigParser's home page is located at:

  http://people.via.ecp.fr/~flo/projects/CondConfigParser/


Requirements
------------

This version of CondConfigParser requires `Python`_ 3.4 or later.

Installation also needs `setuptools`_, but this should only be a concern
if you want to install without `pip`_ (if you have ``pip``, you should
already have ``setuptools``; and if not, installing ``pip`` is likely to
cause ``setuptools`` to be installed at the same time).

.. _Python: https://www.python.org/
.. _pip: https://pypi.python.org/pypi/pip


Quick installation instructions
-------------------------------

If you have a working `pip`_ setup, you should be able to install
CondConfigParser with::

  pip install CondConfigParser

(``pip install condconfigparser`` also works)

When doing so, make sure that your ``pip`` executable runs with the
Python 3 installation you want to install CondConfigParser for.

For more detailed instructions, you can read the ``INSTALL.txt`` file
from a release tarball. You may also want to consult the `“Installing
Python Modules” chapter of the Python documentation
<https://docs.python.org/3/installing/index.html>`_ and the `pip
documentation <https://pip.pypa.io/>`_.


Download
--------

Typical installations with `pip`_ automatically download the latest
release from `PyPI`_. However, in some cases, you may want to download
the tarball or zip file yourself in order to install it later, possibly
on a different machine. In such a case, you may get it `from PyPI
<https://pypi.python.org/pypi/CondConfigParser>`_ or `from Florent
Rougon's home page
<http://people.via.ecp.fr/~flo/projects/CondConfigParser/dist/>`_.

.. _PyPI: https://pypi.python.org/pypi


Git repository
--------------

CondConfigParser is maintained in a `Git repository
<https://github.com/frougon/CondConfigParser>`_ that can be cloned with::

  git clone https://github.com/frougon/CondConfigParser


Documentation
-------------

The CondConfigParser Manual is written in `reStructuredText`_ format for
the `Sphinx`_ documentation generator. The HTML documentation for the
latest version of CondConfigParser as rendered by Sphinx is available
at:

  http://people.via.ecp.fr/~flo/projects/CondConfigParser/doc/

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Python: https://www.python.org/
.. _Sphinx: http://sphinx-doc.org/
.. _LaTeX: http://latex-project.org/
.. _Make: http://www.gnu.org/software/make/

The sources for the CondConfigParser Manual are located in the ``doc``
top-level directory of the CondConfigParser distribution, but the
documentation build process pulls many parts from the source code,
mainly docstrings.

To generate the documentation yourself from CondConfigParser's code and
the `reStructuredText`_ sources in the ``doc`` directory, first make
sure you have `Python`_ 3.x, `Sphinx`_ and `Make`_ installed. Then, go
to the ``doc`` directory and type, for instance::

  make html

You will find the output in the ``_build/html`` subdirectory of ``doc``.
`Sphinx`_ can build the documentation in many other formats. For
instance, if you have `LaTeX`_ installed, you can generate the
CondConfigParser Manual in PDF format with::

  make latexpdf

You can run ``make`` from the ``doc`` directory to see a list of the
available formats. Run ``make clean`` to clean up after the
documentation build process.

Note:

  The ``Makefile`` uses a Python script (``prepare-basic-pkg-info.py``)
  to generate ``basic-pkg-info.rst`` from the top-level ``README.rst``
  file. By default, this script is interpreted by the ``python3``
  executable. If you want to explicitely choose the interpreter to use,
  you can set the ``PYTHON`` Makefile variable like this::

    make PYTHON=python3.4 html

  Note that this only affects running of ``prepare-basic-pkg-info.py``;
  the Python interpreter used by Sphinx in other places of the
  ``Makefile`` is determined by the `sphinx-build`_ executable that
  should be part of your Sphinx installation.

For those who have installed `Sphinx`_ but not `Make`_, it is still
possible to build the documentation with two commands such as::

  python3 prepare-basic-pkg-info.py ../README.rst basic-pkg-info.rst
  sphinx-build -b html -d _build/doctrees . _build/html

These commands must be run from the ``doc`` directory. Please refer to
`sphinx-build`_ for more details.

.. _sphinx-build: http://sphinx-doc.org/invocation.html


Running the automated test suite
--------------------------------

* If you want to run the automated test suite from an unpacked release
  tarball (or `Git`_ checkout), go to the root directory of that
  CondConfigParser distribution (the directory containing ``README.rst``
  and the ``condconfigparser`` directory) and run::

    python3 -m unittest

  (assuming of course that you want to run the tests with an executable
  called ``python3``).

  You may want to add the ``-v`` option at the end of the command in
  order to run the test suite in verbose mode.

* On the other hand, if you have already installed CondConfigParser for
  a given Python installation and you want to test the installed
  package, go to the directory containing the installed package and
  run::

    python3 -m unittest discover -t ..

  With a POSIX-style shell, you can combine both operations with the
  following command (that does not change your current directory)::

    ( cd base_dir/lib/python3.4/site-packages/condconfigparser && \
      python3 -m unittest discover -t .. )

  This command is given for a Python 3.4 installation:

    - rooted at ``base_dir`` (typically ``/usr``, ``/usr/local``,
      ``/opt/pythonX.Y`` [on Unix-like systems] or a directory
      containing a Python `venv`_ or `virtualenv`_)

    - using the ``python3`` executable.

  You may want to add the ``-v`` option after the ``discover`` argument
  in order to run the test suite in verbose mode.

A successful run of the test suite looks like this::

  % python3 -m unittest
  .......
  ----------------------------------------------------------------------
  Ran 7 tests in 0.052s

  OK
  % echo $?
  0
  %

In the above output, each dot represents a successful test. The
``echo $?`` command shows the zero exit status, indicating success for
all tests. In case of a failure, the exit status is non-zero.

It is also possible to ask `setuptools`_ to run the test suite (by
default in verbose mode, cf. `the corresponding documentation
<https://setuptools.pypa.io/en/latest/setuptools.html#test-build-package-and-run-a-unittest-suite>`_).
For instance::

  python3 setup.py test

.. _Git: http://git-scm.com/
.. _venv: https://docs.python.org/3/library/venv.html
.. _virtualenv: https://virtualenv.pypa.io/
.. _setuptools: https://setuptools.pypa.io/

.. 
  # Local Variables:
  # coding: utf-8
  # fill-column: 72
  # End:
