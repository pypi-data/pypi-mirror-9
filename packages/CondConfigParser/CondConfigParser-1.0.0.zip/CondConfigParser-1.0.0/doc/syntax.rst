.. currentmodule:: condconfigparser

Syntax recognized by the parser
===============================

Informal description
--------------------

Generally speaking, the syntax understood by CondConfigParser is inspired by
the Python_ language for comments and expressions, but differs in the overall
structure of a configuration file (variable assignments inside braces,
predicates inside square brackets, etc.).

.. _Python: http://www.python.org/

.. _whitespace-and-comments-rules:

Whitespace and comments
^^^^^^^^^^^^^^^^^^^^^^^

.. _comment-lines:

- Except inside a string literal, any line whose first non-space character is a
  comment sign (``#``) is completely ignored (:dfn:`comment line`).

- If a line contains a comment sign (``#``) that is not inside a string
  literal or a :term:`raw configuration line`, then all characters between the
  comment sign and the end of the line are ignored.

- After or between particular syntactic elements, a newline is required. In
  such a case, several newlines are equivalent to one.

- In general, spaces between keywords, variable names, operators, etc. are
  only used as a separator. Several spaces are equivalent to one space, the
  only exceptions being inside string literals and :term:`raw configuration
  lines <raw configuration line>`.


Continuation lines
^^^^^^^^^^^^^^^^^^

When it is desirable to split a particular syntactic construct onto several
lines, but introducing a newline in this construct would break its syntax, it
is usually possible to end a line with a backslash. In such a case, the parser
will behave as if that line (with the backslash removed) and the next line
were only a single line. This \\<newline> escape sequence can be used on
several consecutive physical lines of the configuration file to make them
appear as a single logical line to the parser.

The only exception to this rule are :term:`raw configuration lines <raw
configuration line>` which, by definition, are so raw that they don't support
this kind of line splitting—however, this can of course be implemented at end
user application level. Example::

  { some_variable = other_variable or \
                    another_one or \
                    "value used if 'other_variable' and 'another_one' \
  are both false in boolean context"

    var = ["with", "opening", "delimiters", "such", "as",
           "[", "and", "(", "this", "is", "not", "necessary."]
    var2 = (example     or
            with        and # 'example', 'with' and 'parentheses'
            parentheses)    # are variable references here!
  }

  [ var and
    not var2 ]   # split predicate
  Exception: raw configuration lines are so "raw" that handling comments and \
  continuation lines is up to the user application. Therefore, we have THREE
  raw configuration lines here, the first of which ends with a backslash.


Supported data types
^^^^^^^^^^^^^^^^^^^^

CondConfigParser currently supports three data types: boolean, string and
list. These types can be used either as literals or in the form of variable
references.

Boolean literals
""""""""""""""""
Boolean literals are written as in Python_. There are exactly two of them:
``True`` and ``False``. Examples::

  foobar = True
  baz = False

String literals
"""""""""""""""
String literals use a similar but more limited syntax than in Python_. The
following escape sequences are recognized:

===============  ===================
Escape sequence  Meaning
===============  ===================
``\\``           ``\``
``\t``           <tab> character
``\n``           <newline> character
``\"``           ``"``
\\<newline>      continuation line
===============  ===================

It is an error if a line ends while a string literal is being read, except if
the last character of the line is a backslash (i.e., the \\<newline> escape
sequence has been used). Examples::

  foo = "simple string"
  bar = "This string contains many escape sequences: \\ \t \n \" \
  (backslash, tab, newline, double quote) and is made of exac\
  tly two lines (see the backslash-n escape sequence near the beginning \
  of the string)."

List literals
"""""""""""""
List literals are written as in Python_, between square brackets. Example::

  foo = [True, False, False, "zaz"]  # This one contains 4 elements

- Lists may be nested at will.

- The elements of a list literal can be written as literals or using variable
  references.

- Since a list literal is only complete when the closing bracket has been
  encountered, it may span multiple lines without any need to use a
  \\<newline> escape sequence.

Example::

  example_list = ["first element", True, some_variable,
                  "fourth element", "fifth element",
                  ["list", "in", "a", "list", other_variable],
                  "last element of the outer list"]

.. _evaluation-in-boolean-context:

Evaluation in boolean context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each literal or variable reference in an expression may be :dfn:`evaluated in
boolean context` in order to determine whether it should be considered true or
false for :token:`orTest`, :token:`andTest`, :token:`notTest` expressions and
:ref:`predicates <predicates>`. The rules for this are the same as in Python_:

  - the literal booleans ``True`` and ``False`` are respectively true and
    false;

  - a string or list is true if, and only if it is not empty.

.. _orTest-expressions-informal:

:token:`orTest` expressions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

An important element of the grammar understood by CondConfigParser is the
:token:`orTest` expression ("non-terminal symbol" in grammar-speak). This is
because :token:`orTest` expressions are the central element of both
:ref:`variable-assignments` and :ref:`predicates <predicates>`.

Roughly speaking, an :token:`orTest` expression is a literal string, list or
boolean, a variable reference or a combination of all these using operators
among ``==``, ``!=``, ``in``, keywords among ``or``, ``and``, ``not``, ``in``,
``True``, ``False`` and parentheses. Examples::

  var1 = True
  var2 = "some string"
  var3 = ["a", "list"]
  var4 = var1              # variable reference
  var5 = not var1
  var6 = var5 and (var1 or (extvar1 and "blabla" in var3)) and \
         var3 == extvar2 and extvar3 != [True, "abc"]

Operators precedence is given in the following table, from lowest precedence
(least binding) to highest precedence (most binding). The  ``or`` and ``and``
operators are left-associative.

======================  =============================
Operator                Description
======================  =============================
``or``                  logical 'or'
``and``                 logical 'and'
``not``                 logical 'not'
``==``, ``!=``, ``in``  equality and membership tests
======================  =============================

The ``in`` operator can be used to test:

  - whether a character (string of length 1) is part of a string;
  - whether an arbitrary object is an element of a list.

(the objects need not be written literally: they can be specified via variable
references)

The ``or`` and ``and`` operators are "short-circuit" operators, as in Python_.
This means that, in an expression such as :samp:`{A} or {B} or {C}`, the
evaluation, from left to right, stops as soon as the result (interpreted as a
boolean) is known. Moreover, the return value is the last subexpression that
was evaluated. For instance, in this example, if *A* is true in boolean
context, then the whole expression :samp:`{A} or {B} or {C}` evaluates to *A*.
Otherwise, *B* is evaluated. If it is true in boolean context, it becomes the
value of the whole expression; otherwise, if *B* is false in boolean context,
then *C* is evaluated and used as the return value. The evaluation procedure
is similar for :token:`andTest` expressions, with the obvious difference that
in this case, the process stops at the first expression that is false in
boolean context.

This property allows a well-known trick::

  variable = other_var or default

If ``other_var`` is true in boolean context, its value is assigned to
``variable``. Otherwise, ``default`` is used.

For a more formal description of :token:`orTest` expressions, see :ref:`below
<formal-grammar>`.

Structure of a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _variable-assignments:

Variable assignments
""""""""""""""""""""

The first syntactic element that may appear in a configuration file understood
by CondConfigParser is a section containing variable assignments. Such a
section is optional and enclosed in braces (``{`` and ``}``). Inside the
braces are a series of variable assignments separated by at least one newline.
Example::

  { favorite_fruits = ["banana", "orange", "mango"]
    worst_fruit = "apple"
    trying_to_be_a_good_boy = False }

Each assignment must have the form :samp:`{variable} = {value}` where
*variable* may contain ASCII letters, digits and underscore characters (``_``)
and *value* is an expression presented :ref:`above
<orTest-expressions-informal>` and defined by the :token:`orTest` production
in the formal grammar described :ref:`below <formal-grammar>`.

The closing brace (``}``) that marks the end of variable assignments **must**
be followed by a newline.

.. rubric:: Order of variable assignments

Variable assignments are performed in the top to bottom order of the
configuration file, as in Python_. As a consequence, after the following
variable assignments::

  { a = "abc"
    b = a
    a = [b] }

the value of ``a`` is ``["abc"]`` and that of ``b`` is ``"abc"``. This is
because ``b`` is assigned the value ``"abc"`` in the second line and that
value is used inside the list when assigning the final value for ``a`` in the
third line.

.. _raw-configuration-line:

.. _default-raw-configuration-lines:

.. _default-unconditional-section:

Default raw configuration lines
"""""""""""""""""""""""""""""""
After the optional :ref:`variable assignments section <variable-assignments>`
(which must be followed by at least one newline) come zero or more :dfn:`raw
configuration lines`. These lines are passed *as is* to the end user
application without any particular processing (hence the *raw* qualifier).
More precisely:

  - a line starting with optional spaces followed by a ``#`` character is
    ignored (:dfn:`comment line`);

  - the first line whose first non-space character is an opening bracket
    (``[``) marks the start of a :ref:`predicate <predicates>` and therefore
    the end of the raw configuration lines.

  - all other lines in-between are passed *verbatim* to the end user
    application. In particular, a line containing a ``#`` character after
    characters that are not all spaces does not receive any special treatment.

The raw configuration lines occurring right after the :ref:`variable
assignments section <variable-assignments>` are not subject to any
:ref:`predicate <predicates>`. For this reason, they are called the
:dfn:`default raw configuration lines` and together form the :dfn:`default,
unconditional section`.

.. _conditional-sections:

Conditional sections
""""""""""""""""""""
After the optional :ref:`default raw configuration lines
<default-raw-configuration-lines>` come zero or more conditional sections. A
:dfn:`conditional section` is composed of a predicate followed by zero or more
raw configuration lines associated with this predicate. Raw configuration
lines have been presented :ref:`earlier <raw-configuration-line>`; let's
introduce predicates now.

.. _predicates:

.. rubric:: Predicates

A :dfn:`predicate` is a boolean expression enclosed in square brackets (``[``
and ``]``). More precisely, the boolean expression must be an :ref:`orTest
expression <orTest-expressions-informal>` and the closing square bracket must
be followed by at least one newline to form a valid predicate.

The predicate may contain references to variables defined either in the
:ref:`variable assignments section <variable-assignments>` or
:term:`externally <external variable>`. It is evaluated every time
:meth:`RawConditionalConfig.eval` is called and its value is interpreted in
:ref:`boolean context <evaluation-in-boolean-context>`. If the predicate is
true, its associated raw configuration lines are said to be :dfn:`applicable`
and are thus included in the output of :meth:`RawConditionalConfig.eval`.
Otherwise, they are not applicable and as such are omitted from the return
value of this method.

.. _formal-grammar:

Formal description: the Grammar
-------------------------------

Presentational conventions for grammar rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the following grammar rules, ε (epsilon) represents the :dfn:`empty word`
and, for a given terminal or non-terminal symbol *A*:

  - :samp:`{A}*` represents zero or more occurences of *A*;
  - :samp:`{A}+` represents one or more occurences of *A*.

A backslash (``\``) at the end of a line in the grammar introduces a
continuation line. It is only used for presentational purposes and has no
meaning for the grammar. Finally, a sequence of characters enclosed in single
quotes (``'``) represents a terminal symbol.

The Grammar
^^^^^^^^^^^

All grammar rules described below are :class:`~condconfigparser.parser.Parser`
rules. They are applied to the output of the
:class:`~condconfigparser.lexer.Lexer`, which implies that whitespace and
comments have already been handled as explained in
:ref:`whitespace-and-comments-rules`.

The general idea is that the config file starts with an optional section
containing :ref:`variable assignments <variable-assignments>`, followed by
:ref:`default raw configuration lines <default-raw-configuration-lines>`
(sometimes called :term:`default options <option>`, and corresponding to
:token:`rawConfigLine` tokens), themselves followed by zero or more
:ref:`sections specifying conditional options <conditional-sections>`.

So, a configuration file in the format recognized by CondConfigParser starts
with an optional :token:`varAssignments` section delimited by braces (``{``
and ``}``), in which an arbitrary number of variables may be defined:

.. productionlist:: parser1
  root             : `varAssignments`? `config`
  varAssignments   : '{' `varAssigs` '}' newline+
  varAssigs        : newline* \
                   :  (ε | `variableAssignment` (newline+ `variableAssignment`)*)
  variableAssignment : variable '=' `orTest`

Following the optional :token:`varAssignments` section comes the
:ref:`"default", unconditional section <default-unconditional-section>`. It is
composed of zero or more :token:`rawConfigLine`\(s\) representing
configuration lines to be parsed by the application using CondConfigParser
(lines starting with optional spaces followed by a ``#`` are ignored as
:ref:`comment lines <comment-lines>`; however, in all other lines, the ``#``
and subsequent characters until the end of the line are passed to the user
application as is). The first line whose first non-space character is an
opening bracket (``[``) marks the start of a :token:`predicate` and therefore
the end of the "default", unconditional section.

After this section come zero or more conditional sections:

.. productionlist:: parser2
  config           : (rawConfigLine*) (`section`)*
  section          : `predicate` (rawConfigLine)*

Implementation note: outside a :token:`predicate`, the lexer transforms an
opening bracket (``[``) into a :token:`predicateStart` token. As long as it is
inside the :token:`predicate` (which depends on the nesting level of square
brackets), opening brackets (``[``) are transformed into :token:`listStart`
tokens and closing brackets (``]``) into :token:`listEnd` tokens. When the
closing bracket (``]``) matching the opening bracket (``[``) that opened the
:token:`predicate` is encountered, the lexer outputs a :token:`predicateEnd`
token.

.. productionlist:: parser3
  predicate        : predicateStart `orTest` predicateEnd newline+
  orTest           : `andTest` ('or' `andTest`)*
  andTest          : `notTest` ('and' `notTest`)*
  notTest          : `atomicBool` | 'not' `notTest`
  atomicBool       : `expr` | `equalsTest` | `notEqualsTest` | `inTest`
  equalsTest       : `expr` '==' `expr`
  notEqualsTest    : `expr` '!=' `expr`
  inTest           : `expr` 'in' `expr`

A :token:`variable` is a sequence of ASCII letters, digits or underscore that
is:

  - delimited by word boundaries (according to the Python :mod:`re` module);
  - not a keyword (``or``, ``and``, ``not``, ``in``, ``True``, ``False``).

.. productionlist:: parser4
  expr             : variable | `literal` | '(' `orTest` ')'
  literal          : stringLiteral | `listLiteral` | `boolLiteral`
  boolLiteral      : 'True' | 'False'
  listLiteral      : listStart (ε | `orTest` (, `orTest`)*) listEnd

As presented here, the grammar is not LL(*k*) for any integer *k*, because of
the :token:`atomicBool` production. However, replacing it with the
:token:`atomicBoolAlt` production below ("left-factoring") does make the
grammar LL(1). This is more or less the approach used in
:mod:`~condconfigparser.parser`, in a way that still allows one to obtain a
nice abstract syntax tree reminding of the grammar presented above.

.. productionlist:: atomicbool-alt
  atomicBoolAlt    : `expr` `atomicBoolEnd`
  atomicBoolEnd    : ε | `equalsTestEnd` | `notEqualsTestEnd` | `inTestEnd`
  equalsTestEnd    : '==' `expr`
  notEqualsTestEnd : '!=' `expr`
  inTestEnd        : 'in' `expr`
