The Iperf Expressions
=====================
.. currentmodule:: iperflexer.iperfexpressions

This module holds a set of regular expressions to help with lexing the iperf input.



.. _iperfexpressions-expression-base:

The ExpressionBase
------------------

The ``ExpressionBase`` is an Abstract Base Class that provides a logger for children and requires that they implement an `expression` property. 

.. ifconfig:: repository != 'rtfd'

   .. uml::

      ExpressionBase -|> BaseClass
      ExpressionBase : String expression
      ExpressionBase : re.RegexObject regex

.. autosummary::
   :toctree: api

   ExpressionBase
   


The HumanExpression
-------------------

This is a concrete implementation of the :ref:`ExpressionBase <iperfexpressions-expression-base>`.

.. ifconfig:: repository != 'rtfd'

   .. uml::

      HumanExpression -|> ExpressionBase
      HumanExpression : String thread_column
      HumanExpression : String expression
      HumanExpression : re.RegexObject regex

.. autosummary::
   :toctree: api

   HumanExpression

The `expression` is composed of parts from :ref:`Oatbran <oatbran-expressions>` so I will not re-define the base components. The following is an approximation of the expression (all the parts that are in all-capital letters are from oatbran, as are the number classes which are used because the latex output is not that easy to read in sphinx):

.. math::

   threads &\gets L\_BRACKET + OPTIONAL\_SPACES + \mathbb{Z} + R\_BRACKET\\
   interval &\gets \mathbb{R} + OPTIONAL\_SPACES + DASH + \mathbb{R} + SPACES + `sec'\\
   transfer &\gets \mathbb{R} + SPACES + [`GKM'] + ? + `Bytes'\\
   bandwidth &\gets \mathbb{R} + SPACES + [`GKM'] + ? + (`bits'| `bytes') + `/sec'\\
   expression  &\gets threads + SPACES + interval + SPACES + transfer + SPACES + bandwidth\\

.. '
   


.. _iperfexpressions-csv-expression:

The CSV Expression
------------------

The `CSVExpression` matches csv-output format (``-y c``).

.. ifconfig:: repository != 'rtfd'

   .. uml::

      CsvExpression -|> ExpressionBase
      CsvExpression : re.RegexObject regex

.. autosummary::
   :toctree: api

   CsvExpression

As with the above, the main regular expressions are defined in the :ref:`oatbran module <oatbran-module>` and the following is just a rough approximation of the regular expression used:

.. math::

   thread &\gets \mathbb{N}\\
   timestamp &\gets \mathbb{Z}\\
   sender\_ip &\gets IP\_ADDRESS\\
   sender\_port &\gets \mathbb{Z}\\
   receiver\_ip &\gets IP\_ADDRESS\\
   receiver\_port &\gets \mathbb{Z}\\
   start &\gets \mathbb{R}\\
   end &\gets \mathbb{R}\\
   interval &\gets start + DASH + end\\
   transfer &\gets \mathbb{Z}\\
   bandwidth &\gets \mathbb{Z}\\
   expression &\gets timestamp + COMMA + sender\_ip + COMMA + sender\_port + COMMA + receiver\_ip + COMMA + receiver\_port + COMMA + thread + COMMA + interval + COMMA + transfer + bandwidth\\



.. _iperfexpressions-combined-expression:

CombinedExpression
------------------

This does not look like it was actually implemented. I think it was a stillborn idea.



Parser Keys
-----------

The `ParserKeys` holds the keys for the `re.match` group dictionaries.

.. ifconfig:: repository != 'rtfd'

   .. uml::

       ParserKeys : units
       ParserKeys : thread
       ParserKeys : start
       ParserKeys : end
       ParserKeys : transfer
       ParserKeys : bandwidth

       ParserKeys : timestamp
       ParserKeys : sender_ip
       ParserKeys : sender_port
       ParserKeys : receiver_ip
       ParserKeys : receiver_port

       ParserKeys : human
       ParserKeys : csv

