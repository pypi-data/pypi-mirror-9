The IperfParser
===============
.. module:: iperflexer.iperfparser

This is the class that performs the work of extracting the data-column.



The `IperfParser` extracts a column from the iperf-output. Currently it only extracts bandwidths or data-transfers. Either it needs to be made more flexible (or a better idea might be to create a family of column extractors). The `IperfParser` is differentiated from the `SumParser` in that it re-adds adds the parallel threads and in-fills zeros for missing time-intervals.

.. warning:: The ``intervals`` and ``transfer_intervals`` are defaultdict objects. This was done so that if an expected interval is missing then a 0 will be returned. As a side, effect, though, if you ask for an interval that didn't exist, you will always get 0, even if it is outside of the range of the data.

.. '

.. uml::

   IperfParser -|> BaseClass
   IperfParser : bandwidths
   IperfParser : regex
   IperfParser : intervals
   IperfParser : conversion
   IperfParser : filename(basename)
   IperfParser : reset()
   IperfParser : pipe(target)
   IperfParser : search(line)
   IperfParser : __call__(line)
   IperfParser : bandwidth(match)
   IperfParser : valid(match)

.. autosummary::
   :toctree: api

   IperfParser
   IperfParser.bandwidths
   IperfParser.transfers
   IperfParser.regex
   IperfParser.intervals
   IperfParser.conversion
   IperfParser.valid
   IperfParser.bandwidth
   IperfParser.__call__
   IperfParser.search
   IperfParser.pipe   
   IperfParser.reset


Properties
----------

bandwidths
~~~~~~~~~~

This is a generator of values from `IperfParser.intervals` in the sorted order of the keys (intervals). It is based on the premise that `IperfParser.intervals` is a dictionary whose keys are the start of the iperf sample intervals. e.g if the samples are reported at 1-second intervals then the keys are traversed :math:`0.0, 1.0,\ldots`.

.. note:: The name of the property suggests that the dictionary values are `bandwidths` but if this class is generalized to extract other columns then this will no longer be true and should be changed.

regex
~~~~~

This is a dictionary holding the regular expressions for the csv-format and the human-readable format. The keys should be accessed through ``iperfexpressions.ParserKeys`` (e.g. ``self.regex[ParserKeys.human]`` to get the regular expression for the human-readable iperf output).
   
