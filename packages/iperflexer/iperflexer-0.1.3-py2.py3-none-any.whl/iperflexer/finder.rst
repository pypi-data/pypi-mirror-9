The Finder
==========

.. currentmodule:: iperflexer.finder

A set of functions to generate filenames, lines in files, lines in sub-sections of files, or count of lines that match an expression for each subsection within files.



Find
----

The `find` takes a glob and finds all matching files.

.. note:: The `find` is recursive so it will match files in sub-folders as well.

.. autosummary:: 
   :toctree: api

   find



Example Use::

    for name in find("*.iperf"):
        print(name)

Concatenate
-----------

The `concatenate` generates all lines from files that match the given glob. It uses the `find` function so it is recursive.

.. autosummary::
   :toctree: api

   concatenate

Example Use::

    for line in concatenate('*csv'):
        process(line)

.. note:: the idea behind the ``concatenate`` is that it allows you to process files that can be grouped by glob, e.g. all files that have `cisco_1250` in their name        



Sections
--------

.. autosummary::
   :toctree: api

   sections

The ``sections`` generator traverses lines from files matching the globs, yielding a generator of lines every time the regular-expression represting the start of the section is matched.



Section Generator
-----------------

The `section` generator generates a subset of lines from an iterator, stopping when a line matches the regular expression representing an end-of-section line.



Line Counter
------------

Traverses a sections within lines, yielding the count of lines that match the `interesting` regular expression for each section.

