The Iperf Lexer (Read Me)
=========================


This is a program to extract bandwidths and data transfers from `iperf <http://sourceforge.net/projects/iperf/>`_ output. To install it you can use pip.

::

   pip install iperflexer

It is meant to be used with files with data-reporting intervals shorter than the total run-time (e.g. 1 second intervals). Once installed it creates a command-line command named ``parseiperf`` and can also be used as a library (see the `SumParser <https://pythonhosted.org//iperflexer/sumparser.html#using-the-sumparser>`_ class documentation for an example of using it this way).

Running It
----------

The original idea behind it was to use it as part of a pipeline so you can pipe iperf output to it directly ::

  iperf -c 192.168.10.5 -i 1 -P 4 | parseiperf

Which will then send the total bandwidth for each interval to standard-output (it does this so that it can then be piped to another command). You can also ``cat`` an existing file to it::

  cat test.iperf | parseiperf

The Command-Line Options
------------------------

You can get a list of the options using the help option.

.. code:: bash

   parseiperf -h

::

    usage: parseiperf [-h] [-g GLOB] [-u UNITS] [-i INTERVAL]
                      [--tolerance TOLERANCE] [-s] [-v] [--pudb] [--pdb] [-t]
                      [-p THREADS] [-m MAXIMUM] [-l] [-d]
    
    optional arguments:
      -h, --help            show this help message and exit
      -g GLOB, --glob GLOB  A file-glob to match input file names. (default=None)
      -u UNITS, --units UNITS
                            Output units per second
                            [bits,Bytes,KBits,KBytes,Mbits,MBytes,Gbits,GBytes]
                            (default=Mbits)
      -i INTERVAL, --interval INTERVAL
                            Reporting intervals (default=1)
      --tolerance TOLERANCE
                            Interval tolerance (if parsed interval differs from
                            expected by more than tolerance, assume summation
                            lines) (default=0.1)
      -s, --save            If glob is provided, save to a file instead of sending
                            to stdout. (default=False)
      -v, --voodoo          Add threads yourself instead of using 'sum' lines.
                            (default=False)
      --pudb                Enable pudb (if installed). (default=False)
      --pdb                 Enable pdb (default=False)
      -t, --tee             Send lines standard error as they come in.
                            (default=False)
      -p THREADS, --threads THREADS
                            Specify thread count (default=4)
      -m MAXIMUM, --maximum MAXIMUM
                            Maximum allowed bandwidth (default=1000000)
      -l, --lastlinebandwidth
                            Get Iperf's final bandwidth value (default=False)
      -d, --lastlinetransfer
                            Get Iperf's final reported data transfer
                            (default=False)
    
    



Glob
~~~~

Although I said above that you pipe input to the ``parseiperf`` command you can also use a file-glob to pass in file-names to it. It descends into all sub-directories to look for matches so you need to make sure the glob is restrictive enough to not match unexpected files and you also need to surround it with quotation marks (so that the shell's interface doesn't expand the glob before passing it to the command). The output for all the files will be concatenated and output to standard output. 

::

   parseiperf -g "*.iperf"

Although my example uses a glob you could just pass in a file name.

Units
~~~~~

The ``--units`` tells the `iperflexer` what units the bandwidths should use. One of the reasons for this code was to allow the iperf raw-data to be output in bits per second and then converted later to the more human-readable Megabits or Gigabits per second. The names for the units is meant to match the iperf headers (so to get megabits-per-second use `Mbits`).

Saves
~~~~~

As noted above, the default behavior is to send output to standard output, concatenating the values for multiple data-files, but if you passed in a file-name-glob you can use the ``--save`` option and it will save the output for each input file to a separate file. The output-file-names will be the input-file-names with `_parsed.csv` appended to them.

VooDoo
~~~~~~

The ``--voodoo`` flag will tell ``iperflexer`` to re-add the individual threads (otherwise it uses the summed-values that iperf provides). In retrospect this should have been the default, but I didn't have a complete enough understanding of how iperf's reporting worked when I created the command-line interface. If you are doing a time-series analysis, the ``--voodoo`` interval sums will catch reporting intervals that are missing their summation lines and so should be considered better for that case. The intervals aren't quiet right for re-calculating the total values though, so you should use the ``--lastlinebandwidth`` and ``--lastlinetransfers`` if you are trying to find the values for the entire session.

Debugging
~~~~~~~~~

The ``--pudb`` and ``--pdb`` options will start the chosen debugger before running the command.

Tee
~~~

The ``--tee`` option tells the command to send the un-parsed iperf lines to standard error. This way if you use it in the originally intended way (piping to another command) you can still see what happened or you can pipe it to another command (including another instance of the ``parseiperf`` command).

Threads
~~~~~~~

By default, it is assumed that only one thread is being used. If more than one thread was used the number of threads has to be specified by passing in the ``--threads`` option. I might change it to make it infer them but I originally chose to do it this way because it seemed safest in the event of incomplete data output.

Maximum
~~~~~~~

Sometimes when the bandwidth gets really small iperf seems to react by generating an unbelievably large number. When the ``iperflexer`` sees a bandwidth that's larger than what's set as the ``--maximum`` (default is :math:`10^6`) it will report the value as 0.

Last Line Bandwidth
~~~~~~~~~~~~~~~~~~~

If set, this will grab the last sum-line whose interval is bigger than the interval given (which is assumed to be the bandwidth-rate that iperf calculated for the session). This will generally be different from the value you would get if you were to re-add the interval counts, especially if any of the threads doesn't report back in time for the interval (it looks like iperf drops the value for the interval's reporting but adds it in once the thread does report back). Since it's usually the last line you could probably get it with some clever `tail` and `sed` combining or some other command-line combination, but this will also convert the units for you and allow you to process a set of files. Suppose you wanted to create a column of the bandwidth summaries for files that start with 'client' and end with 'iperf' and you want to store the outcome in 'client_summaries.csv'. You could do it with::

   parseiperf -g "client*iperf" -l > client_summaries.csv

.. '   

Last Line Transfer
~~~~~~~~~~~~~~~~~~

As you might suspect, this tries to grab the last reported data-transfer (the transfer for the entire interval). It is currently mutually-exclusive to the last line bandwidth. This should be changed eventually. An example to gather the server-side information (assuming the names are meaningful)::

   parseiperf -g "server*iperf" -l > server_transfer_summaries.csv

Interval
~~~~~~~~

The expected reporting interval (e.g. every second is ``-i 1``). If the interval found on a line exceeds the expected interval, then it is assumed to be a total summation line and not used by the interval values, but is used by the SumParser.last_line_bandwidth and last_line_transfer. 

Tolerance
~~~~~~~~~

The amount that the calculated reporting interval is for a line can differ from the expected interval. This was created to prevent float rounding problems, but probably doesn't need to be set.

Building the Documentation
--------------------------

I try to keep an updated build of the documentation on the web at `bitbucket <http://rallion.bitbucket.org/commands/iperf_lexer/index.html>`_ and `pypi <https://pythonhosted.org/iperflexer/>`_ but these instructions should help if you want to build them yourself.

The code was written in a literate programming style using `Pweave <http://mpastell.com/pweave/>`_ so next to each python file you will also find a restructured-text file used for the documentation -- the python package is also the `sphinx <http://sphinx-doc.org/>`_ source for the documentation. If you want to edit or re-generate a file you need pweave::

  pip install pweave

Note that pweave has changed since I started using it, requiring Python 3 style ``print`` functions instead of the older python ``print`` statements so if you install it now some of the files may raise an error when weaving (generating the rst files). I don't *think* they will since I'm using stdout and stderr directly, not printing, but buyer beware.

Pweave itself requires matplotlib if you want to generate the rst files (it's meant to facilitate `reproducible research <http://www.ploscompbiol.org/article/info%3Adoi%2F10.1371%2Fjournal.pcbi.1003285>`_ and it has some conveniences for creating plots with matplotlib). So if you want to create the rst files you need to install it::

   pip install matplotlib

Matplotlib itself requires numpy and they can take a long time to build. If you're not into building them just for this and you have a package manager it's probably better to use it. For debian-based systems::

   sudo apt-get install python-matplotlib

Since it's a sphinx repository you'll of course need sphinx::

   pip install sphinx

I'm using the `alabaster <https://github.com/bitprophet/alabaster>`_ sphinx theme so you need that too::

   pip install alabaster   

At the moment I'm using ``sphinxcontrib-plantuml`` for the UML diagrams. If you want them you'll need both plantuml and the sphinx extension::

   apt-get install plantuml
   apt-get install graphviz
   pip install sphinxcontrib-plantuml   

I think that's everything. If it is, then when you're next to the `Makefile` you can build the (html) documentation with::

   make html

And it will output the html files to ``doc/html``. 

.. note:: I `rsync` the html files to a folder where my apache server can see it so if you build it before I remember to get rid of that in the Makefile you will likely see an error but that shouldn't affect the built documentation (although if just by coincidence you have the exact same file structure as me it might clobber something (sorry)). 

Running the Tests
-----------------

I was originally using python's ``unittest`` module but I've switched over to using ``behave`` and ``pyhamcrest`` so the tests at the top of the package need ``nosetests`` and the tests in the `iperflexer/tests` folder need `behave <https://pypi.python.org/pypi/behave>`_ and `PyHamcrest <https://pypi.python.org/pypi/PyHamcrest>`.

