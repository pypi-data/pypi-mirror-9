Coroutines
==========
.. currentmodule:: iperflexer.coroutine

A module for generic coroutines.



Coroutine Decorator
--------------------

This is a decorator used to start a coroutine.

.. autosummary::
   :toctree: api

   coroutine

Example Use::

    @coroutine
    def printer(target):
        while True:
            output = (yield)
            print output
            target.send(output)

    @coroutine
    def sink(filename):
        out_file = open(filename, 'w')
        while True:
            output = (yield)
            out_file.write(output)

    s = sink("test.txt")
    p = printer(s)
    for line in output:
        p.send(line)
            


The Broadcast
-------------

A coroutine to send the same input to multiple targets.

.. digraph:: broadcast

   s -> B
   B -> t1
   B -> t2
   B -> t3

Example Use::

    s1 = sink('out_1.txt')
    s2 = processor('out_2.csv')
    b = broadcast((s1, s2))
    p = printer(b)
    for line in source:
        p.send(line)

* Here we re-use `sink` and `printer` from the previous example and assume the existence of a `processor` co-routine that transforms the input to comma-separated-values.

.. autosummary::
   :toctree: api

   broadcast
   


The Comma Join
--------------

This coroutine reads in a number of inputs before joining them with a comma and sending the string down the pipeline.

.. autosummary:: 
   :toctree: api

   comma_join

.. digraph:: comma_join

   source -> processor1
   source -> processor2
   source -> processor3
   processor1 -> comma_join
   processor2 -> comma_join
   processor3 -> comma_join
   comma_join -> target
   
Although not evident from the graph, since this is a couroutine I assume that the processors are always called in the same order if the output needs it.



Output Coroutine
----------------

.. autosummary::
   :toctree: api

   output

.. digraph:: output

   source -> pipeline
   pipeline -> output

The `output` does not take a co-routine as an argument so it has to act as a sink. 
   


Comma Append
------------

Takes a stream of input strings and appends strings sent to it to each string (acting like a zip between a generator and an input stream).

.. autosummary::
   :toctree: api

   comma_append



File Output Coroutine
---------------------

The `file_output` acts much like the ``output`` co-routine but assumes that the target is a disk-file and will create it if passed a string instead of an open file.

