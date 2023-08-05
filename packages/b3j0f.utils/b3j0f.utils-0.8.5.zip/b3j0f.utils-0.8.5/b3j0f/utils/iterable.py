# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

"""
Provides tools to manage iterable types
"""

__all__ = ['isiterable', 'ensureiterable', 'first']

from collections import Iterable


def isiterable(element, exclude=None):
    """Check whatever or not if input element is an iterable.

    :param element: element to check among iterable types.
    :param type/tuple exclude: not allowed types in the test.

    :Example:

    >>> isiterable({})
    True
    >>> isiterable({}, exclude=dict)
    False
    >>> isiterable({}, exclude=(dict,))
    False
    """

    # check for allowed type
    allowed = exclude is None or not isinstance(element, exclude)
    result = allowed and isinstance(element, Iterable)

    return result


def ensureiterable(value, iterable=list, exclude=None):
    """Convert a value into an iterable if it is not.

    :param object value: object to convert
    :param type iterable: iterable type to apply (default: list)
    :param type/tuple exclude: types to not convert

    :Example:

    >>> ensureiterable([])
    []
    >>> ensureiterable([], iterable=tuple)
    ()
    >>> ensureiterable('test', exclude=str)
    ['test']
    >>> ensureiterable('test')
    ['t', 'e', 's', 't']
    """

    result = value

    if not isiterable(value, exclude=exclude):
        result = [value]
        result = iterable(result)

    else:
        result = iterable(value)

    return result


def first(iterable, default=None):
    """Try to get input iterable first item or default if iterable is empty.

    :param Iterable iterable: iterable to iterate on.
    :param default: default value to get if input iterable is empty.
    :raises TypeError: if iterable is not an iterable value

    :Example:

    >>> first('test')
    't'
    >>> first([])
    None
    >>> first('', default='test')
    'test'
    """

    # start to get the iterable iterator (raises TypeError if iter)
    iterator = iter(iterable)
    # get first element
    try:
        result = next(iterator)
    except StopIteration:
        # if no element exist, result equals default
        result = default

    return result
