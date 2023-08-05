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
latest version of CondConfigParser as rendered by Sphinx should be
available at:

  http://people.via.ecp.fr/~flo/projects/CondConfigParser/doc/

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx-doc.org/
.. _LaTeX: http://latex-project.org/
.. _Make: http://www.gnu.org/software/make/

The sources for the CondConfigParser Manual are located in the ``doc``
top-level directory of the CondConfigParser distribution, but the
documentation build process pulls many parts from the source code,
mainly docstrings.

To generate the documentation yourself from CondConfigParser's code and
the `reStructuredText`_ sources in the ``doc`` directory, first make
sure you have `Sphinx`_ and `Make`_ installed. Then, you can go to the
``doc`` directory and type, for instance::

  make html

You will then find the output in the ``_build/html`` subdirectory of
``doc``. `Sphinx`_ can build the documentation in many other formats.
For instance, if you have `LaTeX`_ installed, you can generate the
CondConfigParser Manual in PDF format with::

  make latexpdf

You can run ``make`` from the ``doc`` directory to see a list of the
available formats. Run ``make clean`` to clean up after the
documentation build process.

For those who have installed `Sphinx`_ but not `Make`_, it is still
possible to build the documentation with a command such as::

  sphinx-build -b html -d _build/doctrees . _build/html

run from the ``doc`` directory. Please refer to `sphinx-build`_ for more
details.

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
