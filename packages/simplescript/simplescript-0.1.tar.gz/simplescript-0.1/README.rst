
Simple Script
=============

* .. image:: https://pypip.in/version/simplescript/badge.svg?branch=master
    :target: https://pypi.python.org/pypi/simplescript/
    :alt: Latest Version

Make a shell script from a python function. Generates an argument parser for
the function using ``argparse`` by inspecting the function arguments.

.. code:: python

    #! /usr/bin/python
    from simplescript import simplescript

    @simplescript
    def myscript(a_flag=False, a_string="default"):
        """An example script"""
        if a_flag:
            print a_string

Install using pip::

   pip install simplescript
