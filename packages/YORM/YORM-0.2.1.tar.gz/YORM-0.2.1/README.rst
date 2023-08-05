YORM
====

| |Build Status|
| |Coverage Status|
| |Scrutinizer Code Quality|
| |PyPI Version|
| |PyPI Downloads|

YORM provides functions and decorators to enable automatic,
bidirectional, and human-friendly mappings of Python object attributes
to YAML files.

Uses beyond typical object serialization and object mapping include:

-  automatic bidirectional conversion of attributes types
-  attribute creation and type inference for new attributes
-  storage of content in text files optimized for version control
-  custom converters to map complex classes to JSON-compatible types

Getting Started
===============

Requirements
------------

-  Python 3.3+

Installation
------------

YORM can be installed with pip:

::

    $ pip install YORM

Or directly from the source code:

::

    $ git clone https://github.com/jacebrowning/yorm.git
    $ cd yorm
    $ python setup.py install

Basic Usage
===========

Simply take an existing class:

.. code:: python

    class Student:

        def __init__(self, name, school, number, year=2009):
            self.name = name
            self.school = school
            self.number = number
            self.year = year
            self.gpa = 0.0

and define an attribute mapping:

.. code:: python

    from yorm import store_instances, map_attr
    from yorm.standard import String, Integer, Float

    @map_attr(name=String, year=Integer, gpa=Float)
    @store_instances("students/{self.school}/{self.number}.yml")
    class Student: ...

Modifications to an object's mapped attributes:

.. code:: python

    >>> s1 = Student("John Doe", "GVSU", 123)
    >>> s2 = Student("Jane Doe", "GVSU", 456, year=2014)
    >>> s1.gpa = 3

are automatically reflected on the filesytem:

.. code:: bash

    $ cat students/GVSU/123.yml
    name: John Doe
    gpa: 3.0
    school: GVSU
    year: 2009

Modifications and new content in the mapped file:

.. code:: bash

    $ echo "name: John Doe
    > gpa: 1.8
    > year: 2010
    > expelled: true
    " > students/GVSU/123.yml

are automatically reflected in the objects:

.. code:: python

    >>> s1.gpa
    1.8
    >>> s1.expelled
    True

For Contributors
================

Requirements
------------

-  GNU Make:

   -  Windows: http://cygwin.com/install.html
   -  Mac: https://developer.apple.com/xcode
   -  Linux: http://www.gnu.org/software/make (likely already installed)

-  virtualenv: https://pypi.python.org/pypi/virtualenv#installation
-  Pandoc: http://johnmacfarlane.net/pandoc/installing.html
-  Graphviz: http://www.graphviz.org/Download.php

Installation
------------

Create a virtualenv:

::

    $ make env

Run the tests:

::

    $ make test
    $ make tests  # includes integration tests

Build the documentation:

::

    $ make doc

Run static analysis:

::

    $ make pep8
    $ make pep257
    $ make pylint
    $ make check  # includes all checks

Prepare a release:

::

    $ make dist  # dry run
    $ make upload

.. |Build Status| image:: http://img.shields.io/travis/jacebrowning/yorm/master.svg
   :target: https://travis-ci.org/jacebrowning/yorm
.. |Coverage Status| image:: http://img.shields.io/coveralls/jacebrowning/yorm/master.svg
   :target: https://coveralls.io/r/jacebrowning/yorm
.. |Scrutinizer Code Quality| image:: http://img.shields.io/scrutinizer/g/jacebrowning/yorm.svg
   :target: https://scrutinizer-ci.com/g/jacebrowning/yorm/?branch=master
.. |PyPI Version| image:: http://img.shields.io/pypi/v/yorm.svg
   :target: https://pypi.python.org/pypi/yorm
.. |PyPI Downloads| image:: http://img.shields.io/pypi/dm/yorm.svg
   :target: https://pypi.python.org/pypi/yorm
