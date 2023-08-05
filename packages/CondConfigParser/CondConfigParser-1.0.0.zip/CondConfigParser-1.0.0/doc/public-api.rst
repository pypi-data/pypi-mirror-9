.. module:: condconfigparser

Public API
==========

The :class:`~condconfigparser.RawConditionalConfig` class
---------------------------------------------------------

The main component of CondConfigParser's API is the
:class:`~!condconfigparser.RawConditionalConfig` class:

.. autoclass:: condconfigparser.RawConditionalConfig
   :members:
   :special-members: __init__
   :undoc-members:
   :exclude-members: extvars
   :show-inheritance:


Exceptions defined in CondConfigParser
--------------------------------------

The following exceptions are defined in the :mod:`condconfigparser` package
for public use:

.. autoexception:: condconfigparser.error

.. autoexception:: condconfigparser.ParseError
   :show-inheritance:

.. autoexception:: condconfigparser.InvalidUsage
   :show-inheritance:

.. autoexception:: condconfigparser.UndefinedVariablesInAssignmentOrPredicate
   :show-inheritance:

.. autoexception:: condconfigparser.UndefinedVariablesInAssignment
   :show-inheritance:

.. autoexception:: condconfigparser.UndefinedVariablesInPredicate
   :show-inheritance:

.. autoexception:: condconfigparser.InTestTypeError
   :show-inheritance:
