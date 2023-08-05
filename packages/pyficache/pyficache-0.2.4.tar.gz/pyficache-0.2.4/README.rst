|Downloads| |Build Status| |Latest Version| |Supported Python versions|

SYNOPSIS
========

The *pyficache* module allows one to get any line from any file, caching
lines of the file on first access to the file. Although the file may
be any file, the common use is when the file is a Python script since
parsing of the file is done to figure out where the statement
boundaries are.

The routines here may be is useful when a small random sets of lines
are read from a single file, in particular in a debugger to show
source lines.

Summary
-------

.. code:: python

    import pyficache
    lines = pyficache.getlines('/tmp/myprogram.py')
    line = pyficache.getline('/tmp/myprogram.py', 6)
    # Note lines[6] == line if /tmp/myprogram.py has more 6 or more lines

    pyficache.clear_file_cache()
    pyficache.clear_file_cache('/tmp/myprogram.py')
    pyficache.update_cache()   # Check for modifications of all cached files.

Credits
-------

This is a port of the my Ruby linecache_ module which in turn is based
on the Python linecache module.

coverage_ provides the cool stuff to figure out lines where there
statements.

Other stuff
-----------

Author:   Rocky Bernstein <rockyb@rubyforge.net>
License:  Copyright (c) 2009, 2015 Rocky Bernstein. Released under the GNU GPL 3 license

.. _coverage: http://nedbatchelder.com/code/coverage/
.. _linecache: https://rubygems.org/gems/linecache

.. |Downloads| image:: https://pypip.in/download/pyficache/badge.svg
.. |Build Status| image:: https://travis-ci.org/rocky/python2-trepan.svg
   :target: https://travis-ci.org/rocky/pyficache/
.. |Latest Version| image:: https://pypip.in/version/pyficache/badge.svg?text=version
   :target: https://pypi.python.org/pypi/pyficache/
.. |Supported Python versions| image:: https://pypip.in/py_versions/pyficache/badge.svg
   :target: https://pypi.python.org/pypi/pyficache/
