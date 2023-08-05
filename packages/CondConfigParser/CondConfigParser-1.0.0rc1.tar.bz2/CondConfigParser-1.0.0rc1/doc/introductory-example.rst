.. currentmodule:: condconfigparser

.. _introductory-example:

An introductory example
=======================

Let's start with a sample configuration file that could be read with
CondConfigParser::

  { favorite_fruits = ["banana", "orange", "mango"]
    worst_fruit = "apple"
    trying_to_be_a_good_boy = False }

  # Default, unconditional options. The format is up to the application
  # developer, with only one restriction: the first non-blank character of an
  # option line can't be an opening bracket ('['), as this marks the start of a
  # conditional section.
  <rawConfigLine 1>
  <rawConfigLine 2>
  ...

  [ fruit_status == "absent" or fruit_of_the_day == worst_fruit ]
  # Application-specific options for this sad circumstance
  <rawConfigLine A1>
  <rawConfigLine A2>
  ...

  [ fruit_status == "fine" and fruit_of_the_day in favorite_fruits ]
  # Application-specific options for this happy circumstance
  <rawConfigLine B1>
  <rawConfigLine B2>
  ...

  [ [fruit_status, fruit_of_the_day] == ["fine", worst_fruit] and
     trying_to_be_a_good_boy ]
  # Application-specific options to show my good resolutions
  <rawConfigLine C1>
  <rawConfigLine C2>
  ...

This sample file contains a section of variable definitions enclosed in braces
(``{`` and ``}``) in which the user defined three variables:
``favorite_fruits``, ``worst_fruit`` and ``trying_to_be_a_good_boy``. It has a
few unconditional :term:`options <option>` (represented here by
``<rawConfigLine 1>``, ``<rawConfigLine 2>``, etc.) as well as three
conditional sections in which the condition (called *predicate*) is enclosed
in square brackets (``[`` and ``]``). The predicates rely on user-defined
variables as well as on two :term:`external variables <external variable>`
(``fruit_of_the_day`` and ``fruit_status``) that must be provided by the
application using CondConfigParser as part of a dictionary called
:term:`context`.

In order to parse such a file, the application developer can do::

  from condconfigparser import RawConditionalConfig

  config = RawConditionalConfig(input, extvars=("fruit_of_the_day",
                                                "fruit_status"))
  # At this point, CondConfigParser has already checked that the two external
  # variables 'fruit_of_the_day' and 'fruit_status' are enough to allow
  # evaluation of all expressions (variable assignments and predicates)
  # contained in the configuration file given by 'input'.
  variables, applicableConfig = config.eval(context)

where:

  - *input* is an :class:`str` instance or a file-like object opened in text
    mode, from which the configuration can be read;
  - *context* is a dictionary giving the value of each :term:`external
    variable`, for instance::

      context = {"fruit_of_the_day": "mango",
                 "fruit_status": "fine"}

After execution of this code, ``variables`` contains::

  {'favorite_fruits': ['banana', 'orange', 'mango'],
   'fruit_of_the_day': 'mango',
   'fruit_status': 'fine',
   'trying_to_be_a_good_boy': False,
   'worst_fruit': 'apple'}

which gives the computed values of all variables, and ``applicableConfig`` is
the following list::

  [['<rawConfigLine 1>', '<rawConfigLine 2>', '...'],
   ['<rawConfigLine B1>', '<rawConfigLine B2>', '...']]

The first element of this list is always a list containing the default,
unconditional :term:`options <option>`::

  ['<rawConfigLine 1>', '<rawConfigLine 2>', '...']

The rest of ``applicableConfig`` is made of the lists of :term:`raw
configuration lines <raw configuration line>` for each conditional section
that matches the given *context*. In this case, the only conditional section
for which the :term:`predicate` is true is the second one, therefore
``applicableConfig`` has only one more element::

  ['<rawConfigLine B1>', '<rawConfigLine B2>', '...']

which corresponds to the second conditional section of the configuration file.
It is possible to ask :meth:`RawConditionalConfig.eval` to return a flat list
by passing :samp:`{flat}=True` as keyword argument. This is often practical,
however the default behavior is to preserve as much information as possible.

So, to sum things up:

  - the configuration file parsing is done by :class:`RawConditionalConfig`'s
    constructor;

  - once you have a :class:`RawConditionalConfig` instance, you can call its
    :meth:`~RawConditionalConfig.eval` method as many times as you want. Every
    time :meth:`~!RawConditionalConfig.eval` is called, it does two things:

      #. compute the value of each variable based on the values of
         :term:`external variables <external variable>` (specified via the
         *context* parameter to :meth:`~!RawConditionalConfig.eval`);

      #. evaluate each :term:`predicate` in the configuration file based on
         the values computed in the previous step.

    Calling :meth:`RawConditionalConfig.eval` does not imply reparsing of the
    configuration file, it only causes "execution" of the abstract syntax tree
    built by :class:`RawConditionalConfig`\'s constructor.

Two more remarks:

  - The section containing variable assignments on the one hand and the
    conditional sections on the other hand are all optional. As a consequence,
    in the simplest case, the configuration file is only made of :term:`raw
    configuration lines <raw configuration line>` belonging to the default,
    unconditional section.

  - The last :term:`predicate` in our sample configuration file contains the
    following test::

      [fruit_status, fruit_of_the_day] == ["fine", worst_fruit]

    This is a list comparison and works just as in Python: the lists are equal
    if, and only if their elements compare equal one by one. In this case,
    this means the comparison will return ``True`` if, and only if the
    ``fruit_status`` variable is equal to ``"fine"`` and the variables
    ``fruit_of_the_day`` and ``worst_fruit`` are equal.

    As in Python, lists may be nested at will and list comparisons are
    recursive.
