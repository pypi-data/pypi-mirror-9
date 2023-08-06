consoleprinter
==============

Console printer with linenumbers, stacktraces, logging, conversions and
coloring.

Active8 BV Active8 (05-03-15) license: GNU-GPL2

install
-------

.. code:: bash

    pip install consoleprinter

contains
--------

Utility functions for working with commandline applications. Logging
Printing Exception parsing Stacktracing Object reflection printing

usage
-----

.. code:: python

    from consoleprinter import console

    colors = ['black', 'blue', 'cyan', 'default', 'green', 'grey', 'magenta', 'orange', 'red', 'white', 'yellow']

    for color in colors:
        console(color, color=color)

PyCharm
-------

Console detects when run in PyCharm or Intellij, and adds links to the
orinating line

.. code:: python

        if len(suite._tests) == 0:
            console_warning("Can't find tests, looked in test*.py")

\`\ ``bash 2.48 | unittester.py:85 | == | Can't find tests, looked in test*.py | File "/Users/rabshakeh/workspace/unittester/unittester/unittester.py", line 85 (run_unit_test) | ==``

Reflection
----------

.. code:: python

    with zipfile.ZipFile(zippath) as zf:
        for member in zf.infolist():
            console(member)

    .. figure:: res/Screen%20Shot%202015-03-17%20at%2017.45.50.png
       :alt: kindle

       kindle
