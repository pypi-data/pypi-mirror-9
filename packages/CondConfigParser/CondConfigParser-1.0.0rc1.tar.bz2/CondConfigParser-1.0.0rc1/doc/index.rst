.. meta::
   :description: CondConfigParser's documentation
   :keywords: CondConfigParser, Python, configuration, file, conditional,
              boolean, variables, manual

#######################
CondConfigParser Manual
#######################

This manual documents CondConfigParser, a Python library designed to help
Python application developers to parse configuration files. Compared to
well-known modules such as :mod:`configparser` and :mod:`json`, the main
specificity of CondConfigParser is that it allows the end user to define
conditions using boolean operators and specific sections in the configuration
file that are only applied when the corresponding condition is fulfilled.

The configuration file format allows the end user to define variables of type
boolean, string or list. These variables, in addition to :dfn:`external
variables` defined by the application, can be combined with Python-like syntax
to define the conditions (called :dfn:`predicates`) mentioned in the previous
paragraph. You can read the :ref:`introductory-example` section for a concrete
example.

Lists in CondConfigParser may be nested at will. Variable definitions may
refer to previously-defined variables. Predicates can combine ``==``, ``!=``
and ``in`` tests using as many logical ``or``, ``and``, ``not`` operators and
parentheses as necessary. Such "logical expressiveness" (and much more) could
be obtained by reading configuration files interpreted as Python code,
however:

  - the syntax in such a case would not allow the almost-freeform options that
    are permitted by CondConfigParser (where the application chooses how to
    interpret the "options");

  - when an application interprets user configuration files as Python code, it
    exposes its users to some risk in case a malicious user manages to sneak
    code of his choice into a configuration file of the victim (think about
    configuration file snippets copied from Internet forums...).

Regarding the second point in particular, CondConfigParser never uses
:func:`eval` or :func:`exec` to parse configuration files. It should thus be
safe to work with any configuration file, including files prepared by
malicious users.

***********
Main Matter
***********

.. toctree::
   :maxdepth: 2

   basic-pkg-info-toc
   introductory-example
   syntax
   public-api
   internals

.. toctree::
   :hidden:

   glossary


**********
Appendices
**********

* :ref:`glossary`
* :ref:`genindex`
* :ref:`search`
