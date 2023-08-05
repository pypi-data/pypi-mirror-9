b3j0f.utils: utility tools in b3j0f projects
============================================

Common tools useful to b3j0f projects.

.. image:: https://travis-ci.org/b3j0f/utils.svg?branch=master
    :target: https://travis-ci.org/b3j0f/utils

.. image:: https://coveralls.io/repos/b3j0f/utils/badge.png
  :target: https://coveralls.io/r/b3j0f/utils

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Installation
------------

pip install b3j0f.utils

Description
-----------

This library provides a set of generic tools in order to ease development of projects in python >= 2.6.

Provided tools are:

- chaining: manage chaining of function call such as chaining execution in some javascript libraries like jquery or d3.
- iterable: tools in order to manage iterable elements.
- path: python object path resolver, from object to absolute/relative path or the inverse.
- property: (un)bind/find properties in reflective and oop concerns.
- reflect: tools which ease development with reflective concerns.
- runtime: ease runtime execution.
- ut: improve unit tests.
- version: ease compatibility between python version (from 2.x to 3.x).

Examples
--------

Chaining
########

>>> from b3j0f.utils.chaining import Chaining, ListChaining
>>> Chaining("te") += "s" += "t" .content
"test"
>>> ListChaining("test", "example").upper()[-1]
["TEST", "EXAMPLE"]

Iterable
########

>>> from b3j0f.utils.iterable import is_iterable, first
>>> is_iterable(1)
False
>>> is_iterable("aze")
True
>>> is_iterable("aze", exclude=str)
False

>>> first("aze")
"a"
>>> first("", default="test")
"test"

Path
####

>>> from b3j0f.utils.path import lookup, getpath
>>> getpath(lookup)
"b3j0f.utils.path.lookup"
>>> getpath(lookup("b3j0f.utils.path.getpath")
"b3j0f.utils.path.getpath"

Property
########

>>> from b3j0f.utils.property import put_properties, get_properties, del_properties
>>> put_properties(min, {'test': True})
>>> get_properties(min)
{'test': True}
>>> del_properties(min)
>>> get_properties(min)
None

Reflect
#######

>>> from b3j0f.utils.reflect import base_elts, is_inherited
>>> class BaseTest(object):
>>>     def test(self): pass
>>> class Test(BaseTest): pass
>>> class FinalTest(Test): pass
>>> base_elts(FinalTest().test, depth=1)[-1].im_class.__name__
Test
>>> base_elts(FinalTest().test)[-1].im_class.__name__
BaseTest

>>> is_inherited(FinalTest.test)
True
>>> is_inherited(BaseTest.test)
False

Perspectives
------------

- Cython implementation.

Documentation
-------------

http://pythonhosted.org/b3j0f.utils
