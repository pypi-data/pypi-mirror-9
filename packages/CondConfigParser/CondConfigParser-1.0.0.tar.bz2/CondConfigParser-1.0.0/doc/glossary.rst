.. _glossary:

Glossary
========

.. currentmodule:: condconfigparser

.. glossary::

   external variable
      CondConfigParser variable that is defined by the calling application and
      passed as part of a :term:`context` argument to specific
      CondConfigParser methods. A notorious method using a context argument is
      :meth:`RawConditionalConfig.eval`.

      In a configuration file, an external variable can be used in variable
      assignments and :term:`predicates <predicate>` without being itself
      explicitely defined in the configuration file. See
      :ref:`variable-assignments` for more details.

      External variables are a kind of :token:`variable` in the formal grammar
      (which does not distinguish them from other variables).

   context
      Mapping from :term:`external variable` names to their values. Such a
      mapping is passed by the application using CondConfigParser to methods
      such as :meth:`RawConditionalConfig.eval`. The context needs not be the
      same during the life of a :class:`RawConditionalConfig` instance: the
      configuration file can be evaluated for different combinations of the
      values of :term:`external variables <external variable>`.

   predicate
      Boolean expression enclosed in square brackets (``[`` and ``]``).

      Each conditional section of the configuration file starts with a
      predicate. If, in a given :term:`context`, the predicate for a given
      section is true, its :term:`raw configuration lines <raw configuration
      line>` are considered to be :term:`applicable <applicable configuration
      line>` and methods such as :meth:`RawConditionalConfig.eval` include
      them in their output. Otherwise, the raw configuration lines are
      normally ignored.

      See :ref:`conditional-sections` for an informal description of the role
      of predicates in the configuration file format and :token:`predicate`
      for the definition in the formal grammar.

   raw configuration line
   option
      A line of the configuration file that is not processed by
      CondConfigParser, except for the removal of leading spaces. Such lines
      are passed to the calling application or ignored depending on whether
      the :term:`predicate` of the section that contains them is true or
      false.

      Raw configuration lines are sometimes called :dfn:`options` because in
      the application for which CondConfigParser was written (`FGo!`_), each
      such line corresponds to an option for the :program:`fgfs` executable
      (which belongs to FlightGear_). It is also more convenient to talk about
      "default, unconditional options" and "conditional options" than it is
      using the equivalent expressions based on the longer phrase "raw
      configuration lines".

      .. _FGo!: https://sites.google.com/site/erobosprojects/flightgear/add-ons/fgo
      .. _FlightGear: http://www.flightgear.org/

      See :ref:`raw-configuration-line` for a description of how raw
      configuration lines are recognized and :token:`rawConfigLine` for use in
      the formal grammar.

   applicable configuration line
      :term:`raw configuration line` belonging to a section whose
      :term:`predicate` is true in a given :term:`context`.

      The main point of :meth:`RawConditionalConfig.eval` (and to a larger
      extent of CondConfigParser) is to evaluate the predicate of each section
      of the configuration file in order to return the applicable
      configuration lines.
