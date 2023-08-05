The Argument Parser
===================


.. currentmodule:: iperflexer.argumentparser

The ArgumentParser provides the main user interface to the *IperfLexer*.

.. _argumentparser-arguments-class:

The Arguments Class
-------------------

This was originally called the `ArgumentParser` but re-named `Arguments` so as not to be confused with the python `ArgumentParser`. Its only real purpose is to separate the defining of the command-line arguments from the ``main`` module so that it can be documented a little better and possibly swapped out later for docopt without needing to clobber it entirely.

.. ifconfig:: repository != 'rtfd'

    .. uml::
    
       Arguments o-- argparse.ArgumentParser
       Arguments : Namespace parse_args()

.. autosummary::
   :toctree: api

   Arguments

Example Use::

   parser = Arguments()
   args = parser.parse_args()


.. _argumentparser-command-line-arguments:
   
Command Line Arguments
----------------------

This is a dump of the ``parseiperf --help`` output.

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
    
    



.. note:: The short-form of the `threads` argument is `p`, not `t` to match *iperf's* '--parallel' and avoid the *parseiperf's* '--tee'.

   
