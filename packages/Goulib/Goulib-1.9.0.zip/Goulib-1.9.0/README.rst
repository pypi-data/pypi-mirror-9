Goulib
======

library of useful Python code for scientific + technical applications

see the `IPython notebook <http://nbviewer.ipython.org/github/Goulu/Goulib/blob/master/notebook.ipynb>`_ for an overview of features

.. image:: https://pypip.in/license/Goulib/badge.png
    :target: https://github.com/goulu/Goulib/blob/master/LICENSE.TXT
    :alt: License
.. image:: https://pypip.in/version/Goulib/badge.png
    :target: https://pypi.python.org/pypi/Goulib/
    :alt: Version
.. image:: https://travis-ci.org/goulu/Goulib.png?branch=master
    :target: https://travis-ci.org/goulu/Goulib
    :alt: Build
.. image:: https://coveralls.io/repos/goulu/Goulib/badge.png
  :target: https://coveralls.io/r/goulu/Goulib
  :alt: Tests
.. image:: https://readthedocs.org/projects/goulib/badge/?version=latest
  :target: http://goulib.readthedocs.org/en/latest/
  :alt: Doc
.. image:: https://www.ohloh.net/accounts/543923/widgets/account_tiny.gif
	:target: https://www.ohloh.net/accounts/543923?ref=Tiny
.. image:: https://api.coderwall.com/goulu/endorsecount.png
    :target: https://coderwall.com/goulu
  
:author: Philippe Guglielmetti goulib@goulu.net
:installation: "pip install Goulib"
:distribution: https://pypi.python.org/pypi/Goulib
:documentation: https://goulib.readthedocs.org/
:notebook: http://nbviewer.ipython.org/github/Goulu/Goulib/blob/master/notebook.ipynb
:source: https://github.com/goulu/Goulib

Modules
-------

**colors**
	hex RGB colors and related functions
**datetime2**
	additions to datetime standard library
**decorators**
	useful decorators
**drawing**
	Read/Write and handle vector graphics in .dxf, .svg and .pdf formats
**expr**
	simple symbolic math expressions
**geom**
	2D + 3D geometry
**graph**
	efficient Euclidian Graphs for `NetworkX <http://networkx.github.io/>`_ and related algorithms
**interval**
	operations on [x..y[ intervals
**itertools2**
	additions to itertools standard library
**markup**
	simple HTML/XML generation (forked from `markup <http://pypi.python.org/pypi/markup/>`_)
**math2**
	additions to math standard library
**motion**
	functions of time which provide (position, velocity, acceleration, jerk) tuples
**optim**
	optimization algorithms : knapsack, traveling salesman, simulated annealing
**piecewise**
	piecewise-defined functions
**polynomial**
	manipulation of polynomials, forked from http://code.activestate.com/recipes/362193-manipulate-simple-polynomials-in-python/ by Rick Muller
**stats**
    very basic statistics functions
**table**
	Table class with Excel + CSV I/O, easy access to columns, HTML output, and much more.
**tests**
    utilities for unit tests (using nose)
**workdays**
	WorkCalendar class with datetime operations on working hours
	merges and improves `BusinessHours <http://pypi.python.org/pypi/BusinessHours/>`_ and `workdays <http://pypi.python.org/pypi/workdays/>`_ packages

Requirements
------------

Goulib uses lazy requirements.
Many modules and functions do not require any other packages,
packages listed in requirements.txt are needed only by some Goulib classes or functions