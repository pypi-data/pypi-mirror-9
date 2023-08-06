#####################################################################
#                                                                   #
# __init__.py                                                       #
#                                                                   #
# Copyright 2014, Chris Billington                                  #
#                                                                   #
# This file is part of the bprofile project (see                    #
# https://bitbucket.org/cbillington/bprofile) and is licensed under #
# the Simplified BSD License. See the LICENSE.txt file in the root  #
# of the project for the full license.                              #
#                                                                   #
#####################################################################

from .bprofile import BProfile
try:
    from __version__ import __version__
except ImportError:
    __version__ = None

__doc__ = r""" `bprofile` is a wrapper around `cProfile`, `gprof2dot` and
    `graphviz`, providing a simple context manager for profiling sections of
    Python code and producing visual graphs of profiling results. It works on
    Windows and Unix.

    `View on PyPI <http://pypi.python.org/pypi/bprofile>`_
    | `Get the source from BitBucket <http://bitbucket.org/cbillington/bprofile>`_
    | `Read the docs at readthedocs <http://bprofile.readthedocs.org>`_

    *************
    Installation
    *************

    to install `bprofile`, run:

    .. code-block:: bash

        $ pip install bprofile

    or to install from source:

    .. code-block:: bash

        $ python setup.py install

    .. note::

        `bprofile` requires `graphviz <http://www.graphviz.org/Download.php>`_
        to be installed. `bprofile` looks for a `graphviz` installation folder
        in ``C:\Program Files`` or ``C:\Program Files (x86)`` on Windows, and
        for `graphviz` executables in the ``PATH`` on Unix.

    *************
    Introduction
    *************

    Every time I need to profile some Python code I go through the same steps:
    looking up `cProfile`'s docs, and then reading about `gprof2dot` and `graphviz`.
    And then it turns out the code I want to profile is a GUI callback or
    something, and I don't want to profile the whole program because it spends
    most of its time doing nothing.

    `cProfile` certainly has this functionality, which I took one look
    at, and thought: *This should be a context manager, and when it exits, it
    should call gprof2dot and graphviz automatically so I don't have to
    remember their command line arguments, and so I don't accidentally print a
    .png to standard output and have to listen to all the ASCII beep
    characters.*

    :class:`BProfile` provides this functionality.


    *************
    Example usage
    *************

    .. code-block:: python

        # example.py

        import os
        import time
        import pylab as pl
        from bprofile import BProfile

        def do_some_stuff():
            for i in range(100):
                time.sleep(.01)

        def do_some_stuff_that_wont_be_profiled():
            os.system('ping -c 5 google.com')

        def do_some_more_stuff(n):
            x = pl.rand(100000)
            for i in range(100):
                time.sleep(.01)
                x = pl.fft(x)


        profiler = BProfile('example.png')

        with profiler:
            do_some_stuff()

        do_some_stuff_that_wont_be_profiled()

        with profiler:
            do_some_more_stuff(5)


    The above outputs the following image ``example.png`` in the current
    working directory:

    .. image:: example.png

    see  :class:`BProfile` for more information on usage.

    """

__all__ = ['BProfile']
