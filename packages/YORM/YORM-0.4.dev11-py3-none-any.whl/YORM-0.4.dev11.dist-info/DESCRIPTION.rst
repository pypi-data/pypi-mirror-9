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

Changelog
=========

0.4 (dev)
---------

- Moved all converters into the `yorm.converters` package.
- Rename `Converter` to `Convertible`.
- Remove the context manager in mapped objects.
- Fixed automatic mapping of nested attributes.

0.3.2 (2015-04-07)
------------------

- Fixed object overwrite when calling `utilities.update`.

0.3.1 (2015-04-06)
------------------

- Fixed infinite recursion with properties that rely on other mapped attributes.

0.3 (2015-03-10)
----------------

- Updated mapped objects to only read from the filesystem if there are changes.
- Renamed `store` to `sync_object`.
- Renamed `store_instances` to `sync_instances`.
- Renamed `map_attr` to `attr`.
- Added `sync` to call `sync_object` or `sync_instances` as needed.
- Added `update_object` and `update_file` to force syncrhonization.
- Added `update` to call `update_object` and/or `update_file` as needed.

0.2.1 (2015-02-12)
------------------

- Container types now extend their builtin type.
- Added `None<Type>` extended types with `None` as a default.
- Added `AttributeDictionary` with keys available as attributes.
- Added `SortedList` that sorts when dumped.

0.2 (2014-11-30)
----------------

- Allowing `map_attr` and `store` to be used together.
- Allowing `Dictionary` containers to be used as attributes.
- Fixed method resolution order for modified classes.
- Added a `yorm.settings.fake` option to bypass the filesystem.

0.1.1 (2014-10-20)
------------------

- Fixed typos in examples.

0.1 (2014-09-29)
----------------

 - Initial release.


