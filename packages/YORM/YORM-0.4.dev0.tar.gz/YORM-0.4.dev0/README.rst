YORM
====

Enables automatic, bidirectional, human-friendly mappings of object
attributes to YAML files.

| |Build Status|
| |Coverage Status|
| |Scrutinizer Code Quality|
| |PyPI Version|
| |PyPI Downloads|

Uses beyond typical object serialization and relational mapping include:

-  bidirectional conversion between basic YAML and Python types
-  attribute creation and type inference for new attributes
-  storage of content in text files optimized for version control
-  extensible converters to customize formatting on complex classes

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

or directly from the source code:

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

    import yorm
    from yorm.standard import String, Integer, Float

    @yorm.attr(name=String, year=Integer, gpa=Float)
    @yorm.sync("students/{self.school}/{self.number}.yml")
    class Student:
        ...

Modifications to each object's mapped attributes:

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

Modifications and new content in each mapped file:

.. code:: bash

    $ echo "name: John Doe
    > gpa: 1.8
    > year: 2010
    > expelled: true
    " > students/GVSU/123.yml

are automatically reflected in their corresponding object:

.. code:: python

    >>> s1.gpa
    1.8
    >>> s1.expelled
    True

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
