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
from b3j0f.utils.path import lookup, clearcache, incache, getpath


class LookUpTest(UTCase):

    def setUp(self):
        pass

    def test_builtin(self):
        """
        Test lookup of builtin
        """

        _open = lookup('%s.open' % open.__module__)
        self.assertIs(_open, open)

    def test_package(self):
        """
        Test lookup package
        """

        package_path = 'b3j0f'
        package = lookup(package_path)
        self.assertEqual(package.__name__, package_path)

    def test_module(self):
        """
        Test lookup of module
        """

        module_path = 'b3j0f.utils'
        module = lookup(module_path)
        self.assertEqual(module.__name__, module_path)

    def test_class(self):
        """
        Test lookup class
        """

        cls = lookup('b3j0f.utils.test.path.LookUpTest')
        self.assertIs(cls, LookUpTest)

    def test_function(self):
        """
        Test lookup function
        """

        f = lookup('b3j0f.utils.path.lookup')
        self.assertIs(f, lookup)

    def test_method(self):
        """
        Test lookup method
        """

        m = lookup('b3j0f.utils.test.path.LookUpTest.test_method')
        self.assertEqual(m, LookUpTest.test_method)

    def test_local(self):
        """
        Test lookup local
        """

        def f_test():
            pass

        l = lookup('f_test')
        self.assertIs(l, f_test)

    def test_notfound(self):
        """
        Test lookup on not existing element
        """

        self.assertRaises(ImportError, lookup, 'unexist')

    def test_cache(self):
        """
        Test lookup cache
        """

        # check if cache is empty
        path = 'b3j0f'
        self.assertFalse(incache(path))
        # check if element is saved in the cache
        lookup(path, cache=True)
        self.assertTrue(incache(path))
        # check if clear cache works
        clearcache(path)
        self.assertFalse(incache(path))
        # check if clear all cache works
        lookup(path, cache=True)
        clearcache()
        self.assertFalse(incache(path))
        # check if element is not saved in the cache
        lookup(path, cache=False)
        self.assertFalse(incache(path))


class GetPathTest(UTCase):

    def test_builtin(self):
        """
        Test getpath builtin
        """

        open_path = getpath(open)
        self.assertEqual(open_path, '%s.open' % open.__module__)

    def test_class(self):
        """
        Test getpath class
        """

        cls_path = getpath(GetPathTest)
        self.assertEqual(cls_path, 'b3j0f.utils.test.path.GetPathTest')


class LookUpGetPathTest(UTCase):

    def test_lookup_getpath(self):
        """
        Test lookup + getpath
        """

        path = '%s.open' % open.__module__
        open_path = getpath(lookup(path))
        self.assertEqual(open_path, path)

    def test_getpath_lookup(self):
        """
        Test getpath + lookup
        """

        f = open
        _open = lookup(getpath(f))
        self.assertIs(_open, f)


if __name__ == '__main__':
    main()
