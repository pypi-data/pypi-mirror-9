#!/usr/bin/env python
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

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.utils.iterable import first, ensureiterable, isiterable
from b3j0f.utils.version import basestring


class EnsureIterableTest(UTCase):

    def test_list(self):

        l = []
        itererable = ensureiterable(l)
        self.assertEqual(itererable, l)

    def test_dict(self):

        l = []
        iterable = ensureiterable(l, iterable=dict)
        self.assertTrue(isinstance(iterable, dict))
        self.assertFalse(iterable)

    def test_exclude(self):

        l = ""
        iterable = ensureiterable(l, exclude=basestring)
        self.assertTrue(iterable)


class IsIterable(UTCase):

    def test_iterable(self):
        """
        Test an iterable value
        """

        self.assertTrue(isiterable([]))

    def test_exclude(self):
        """
        Test iterable and not allowed types
        """

        self.assertFalse(isiterable([], exclude=list))

    def test_excludes(self):
        """
        Test iterable with a tuple of exclude types
        """

        self.assertFalse(isiterable([], exclude=(list, basestring)))

    def test_not_iterable(self):
        """
        Test not iterable element
        """

        self.assertFalse(isiterable(None))


class First(UTCase):

    def test_empty(self):
        """
        Test empty iterable
        """

        self.assertIs(first([]), None)

    def test_first(self):
        """
        Test first element in an iterable
        """

        value = 'value'
        iterable = [value]

        self.assertIs(first(iterable), value)

    def test_default(self):
        """
        Test default value
        """

        default = 'default'

        self.assertIs(first([], default), default)

    def test_notiterable(self):
        """
        Test not iterable
        """

        self.assertRaises(TypeError, first, True)

if __name__ == '__main__':
    main()
