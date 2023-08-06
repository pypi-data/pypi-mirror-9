Comparable
==========

| |Build Status|
| |Coverage Status|
| |Scrutinizer Code Quality|
| |PyPI Version|
| |PyPI Downloads|

Comparable is a library providing abstract base classes that enable
subclasses to be compared for "equality" and "similarity" based on their
attributes.

Getting Started
===============

Requirements
------------

-  Python 3.3+

Installation
------------

Comparable can be installed with pip:

::

    $ pip install comparable

or directly from the source code:

::

    $ git clone https://github.com/jacebrowning/comparable.git
    $ cd comparable
    $ python setup.py install

Basic Usage
===========

After installation, abstract base classes can be imported from the
package:

::

    $ python
    >>> import comparable
    >>> comparable.__version__
    >>> from comparable import SimpleComparable, CompoundComparable

Comparable classes use ``==`` as the operation for "equality" and ``%``
as the operation for "similarity". They may also override a
``threshold`` attribute to set the "similarity" ratio.

Simple Comparables
------------------

Simple comparable types must override the ``equality`` and
``similarity`` methods to return bool and Similarity objects,
respectively. See ``comparable.simple`` for examples.

Compound Comparables
--------------------

Compound comparable types contain multiple simple comparable types. They
must override the ``attributes`` property to define which attributes
should be used for comparison. See ``comparable.compund`` for examples.

Examples
========

Comparable includes many generic comparable types:

::

    $ python
    >>> from comparable.simple import Number, Text, TextEnum, TextTitle
    >>> from comparable.compound import Group

A basic script might look similar to the following:

::

    from comparable.simple import TextTitle
    from comparable import tools

    base = TextTitle("The Cat and the Hat")
    items = [TextTitle("cat & hat"), TextTitle("cat & the hat")]

    print("Equality: {}".format(base == items[0]))
    print("Similarity: {}".format(base % items[0]))

    print("Duplicates: {}".format(tools.duplicates(base, items)))

For Contributors
================

Requirements
------------

-  Make:

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

.. |Build Status| image:: http://img.shields.io/travis/jacebrowning/comparable/master.svg
   :target: https://travis-ci.org/jacebrowning/comparable
.. |Coverage Status| image:: http://img.shields.io/coveralls/jacebrowning/comparable/master.svg
   :target: https://coveralls.io/r/jacebrowning/comparable
.. |Scrutinizer Code Quality| image:: http://img.shields.io/scrutinizer/g/jacebrowning/comparable.svg
   :target: https://scrutinizer-ci.com/g/jacebrowning/comparable/?branch=master
.. |PyPI Version| image:: http://img.shields.io/pypi/v/Comparable.svg
   :target: https://pypi.python.org/pypi/Comparable
.. |PyPI Downloads| image:: http://img.shields.io/pypi/dm/Comparable.svg
   :target: https://pypi.python.org/pypi/Comparable
