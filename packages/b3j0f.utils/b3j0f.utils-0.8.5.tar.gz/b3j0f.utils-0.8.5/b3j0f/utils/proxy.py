# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
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

__all__ = ['get_proxy', 'proxify_routine', 'proxify_elt', 'is_proxy']

"""Module in charge of creating proxies like the design pattern ``proxy``.

A proxy is based on a callable element. It respects its signature but not the
implementation.
"""

from time import time

from functools import wraps

from types import MethodType, FunctionType

from opcode import opmap

from inspect import (
    getmembers, isroutine, ismethod, getargspec, getfile, isbuiltin, isclass
)

from b3j0f.utils.version import PY2, PY3, basestring
from b3j0f.utils.path import lookup

# consts for interception loading
LOAD_GLOBAL = opmap['LOAD_GLOBAL']
LOAD_CONST = opmap['LOAD_CONST']

#: list of attributes to set after proxifying a function
WRAPPER_ASSIGNMENTS = ['__doc__', '__name__']
#: list of attributes to update after proxifying a function
WRAPPER_UPDATES = ['__dict__']
#: lambda function name
__LAMBDA_NAME__ = (lambda: None).__name__
#: proxy class name
__PROXY_CLASS__ = 'Proxy'
#: attribute name for proxified element
__PROXIFIED__ = '__proxified__'


def proxify_elt(elt, bases=None, _dict=None):
    """Proxify a class with input elt.

    :param elt: elt to proxify.
    :param bases: elt class base classes.
    :param _dict: elt class content.
    :return: proxified element.
    :raises: TypeError if elt does not implement all routines of bases and
    _dict.
    """

    # ensure _dict is a dictionary
    _dict = {} if _dict is None else _dict.copy()
    # ensure bases is a tuple of types
    if bases is None:
        bases = ()
    elif isinstance(bases, basestring):
        bases = (lookup(bases),)
    elif isclass(bases):
        bases = (bases,)
    else:  # fill _dict with routines of bases
        bases = tuple(bases)
        for base in bases:
            for name, member in getmembers(base, lambda m: isroutine(m)):
                if not hasattr(elt, name):
                    raise TypeError(
                        "Wrong elt {0}. Must implement {1} ({2}) of {3}".
                        format(elt, name, member, base)
                    )
                if name not in _dict:
                    _dict[name] = member
    # proxify _dict
    for name in _dict:
        value = _dict[name]
        if not hasattr(elt, name):
            raise TypeError(
                "Wrong elt {0}. Must implement {1} ({2})".format(
                    elt, name, value
                )
            )
        if isroutine(value):
            routine_proxy = proxify_routine(value)
            _dict[name] = routine_proxy
    # generate a new proxy class
    cls = type('Proxy', bases, _dict)
    # delete initialization methods
    try:
        delattr(cls, '__new__')
    except AttributeError:
        pass
    try:
        delattr(cls, '__init__')
    except AttributeError:
        pass
    # instantiate proxy cls
    result = cls()
    # bind elt to proxy
    setattr(result, __PROXIFIED__, elt)

    return result


def proxify_routine(routine, impl=None):
    """Proxify a routine with input impl.

    :param routine: routine to proxify.
    :param impl: new impl to use. If None, use routine.
    """

    # init impl
    impl = routine if impl is None else impl

    try:
        __file__ = getfile(routine)
    except TypeError:
        __file__ = '<string>'

    isMethod = ismethod(routine)
    if isMethod:
        function = routine.__func__
    else:
        function = routine

    # flag which indicates that the function is not a pure python function
    # and has to be wrapped
    wrap_function = not hasattr(function, '__code__')

    try:
        # get params from routine
        args, varargs, kwargs, _ = getargspec(function)
    except TypeError:
        # in case of error, wrap the function
        wrap_function = True

    if wrap_function:
        # if function is not pure python, create a generic one
        # with assignments
        assigned = []
        for wrapper_assignment in WRAPPER_ASSIGNMENTS:
            if hasattr(function, wrapper_assignment):
                assigned.append(wrapper_assignment)
        # and updates
        updated = []
        for wrapper_update in WRAPPER_UPDATES:
            if hasattr(function, wrapper_update):
                updated.append(wrapper_update)

        @wraps(function, assigned=assigned, updated=updated)
        def function(*args, **kwargs):
            pass

    # get params from routine wrapper
    args, varargs, kwargs, _ = getargspec(function)

    # get params from routine
    name = function.__name__

    # flag for lambda function
    isLambda = __LAMBDA_NAME__ == function.__name__
    if isLambda:
        name = '_{0}'.format(int(time()))

    # get join method for reducing concatenation time execution
    join = "".join

    # default indentation
    indent = '    '

    if isLambda:
        newcodestr = "{0} = lambda ".format(name)
    else:
        newcodestr = "def {0}(".format(name)

    if args:
        newcodestr = join((newcodestr, "{0}".format(args[0])))
    for arg in args[1:]:
        newcodestr = join((newcodestr, ", {0}".format(arg)))

    if varargs is not None:
        if args:
            newcodestr = join((newcodestr, ", "))
        newcodestr = join((newcodestr, "*{0}".format(varargs)))

    if kwargs is not None:
        if args or varargs is not None:
            newcodestr = join((newcodestr, ", "))
        newcodestr = join((newcodestr, "**{0}".format(kwargs)))

    # insert impl call
    if isLambda:
        newcodestr = join((newcodestr, ": impl("))
    else:
        newcodestr = join((
            newcodestr,
            "):\n{0}return impl(".format(indent))
        )

    if args:
        newcodestr = join((newcodestr, "{0}".format(args[0])))
    for arg in args[1:]:
        newcodestr = join((newcodestr, ", {0}".format(arg)))

    if varargs is not None:
        if args:
            newcodestr = join((newcodestr, ", "))
        newcodestr = join((newcodestr, "*{0}".format(varargs)))

    if kwargs is not None:
        if args or varargs is not None:
            newcodestr = join((newcodestr, ", "))
        newcodestr = join((newcodestr, "**{0}".format(kwargs)))

    newcodestr = join((newcodestr, ")\n"))

    # compile newcodestr
    code = compile(newcodestr, __file__, 'single')

    # define the code with the new function
    _globals = {}
    exec(code, _globals)

    # get new code
    newco = _globals[name].__code__

    # get new consts list
    newconsts = list(newco.co_consts)

    if PY3:
        newcode = list(newco.co_code)
    else:
        newcode = map(ord, newco.co_code)

    consts_values = {'impl': impl}

    # change LOAD_GLOBAL to LOAD_CONST
    index = 0
    newcodelen = len(newcode)
    while index < newcodelen:
        if newcode[index] == LOAD_GLOBAL:
            oparg = newcode[index + 1] + (newcode[index + 2] << 8)
            name = newco.co_names[oparg]
            if name in consts_values:
                const_value = consts_values[name]
                if const_value in newconsts:
                    pos = newconsts.index(const_value)
                else:
                    pos = len(newconsts)
                    newconsts.append(consts_values[name])
                newcode[index] = LOAD_CONST
                newcode[index + 1] = pos & 0xFF
                newcode[index + 2] = pos >> 8
        index += 1

    # get code string
    codestr = bytes(newcode) if PY3 else join(map(chr, newcode))

    # get vargs
    vargs = [
        newco.co_argcount, newco.co_nlocals, newco.co_stacksize,
        newco.co_flags, codestr, tuple(newconsts), newco.co_names,
        newco.co_varnames, newco.co_filename, newco.co_name,
        newco.co_firstlineno, newco.co_lnotab,
        function.__code__.co_freevars,
        newco.co_cellvars
    ]
    if PY3:
        vargs.insert(1, newco.co_kwonlyargcount)

    # instanciate a new code object
    codeobj = type(newco)(*vargs)
    # instanciate a new function
    if function is None or isbuiltin(function):
        result = FunctionType(codeobj, {})
    else:
        result = type(function)(
            codeobj, function.__globals__, function.__name__,
            function.__defaults__, function.__closure__
        )
    # set wrapping assignments
    for wrapper_assignment in WRAPPER_ASSIGNMENTS:
        try:
            value = getattr(function, wrapper_assignment)
        except AttributeError:
            pass
        else:
            setattr(result, wrapper_assignment, value)
    # set proxy module
    result.__module__ = proxify_routine.__module__
    # update wrapping updating
    for wrapper_update in WRAPPER_UPDATES:
        try:
            value = getattr(function, wrapper_update)
        except AttributeError:
            pass
        else:
            getattr(result, wrapper_update).update(value)

    # set proxyfied element on proxy
    setattr(result, __PROXIFIED__, routine)

    if isMethod:  # create a new method
        args = [result, routine.__self__]
        if PY2:
            args.append(routine.im_class)
        result = MethodType(*args)

    return result


def get_proxy(elt, bases=None, _dict=None):
    """Get proxy from an elt.

    :param elt: elt to proxify.
    :type elt: object or function/method
    :param bases: base types to enrich in the result cls if not None.
    :param _dict: class members to proxify if not None.
    """

    if isroutine(elt):
        result = proxify_routine(elt)

    else:  # in case of object, result is a Proxy
        result = proxify_elt(elt, bases=bases, _dict=_dict)

    return result


def proxified_elt(proxy):
    """Get proxified element.

    :param proxy: proxy element from where get proxified element.
    :return: proxified element. None if proxy is not proxified.
    """

    if ismethod(proxy):
        proxy = proxy.__func__
    result = getattr(proxy, __PROXIFIED__, None)

    return result


def is_proxy(elt):
    """Return True if elt is a proxy.

    :param elt: elt to check such as a proxy.
    :return: True iif elt is a proxy.
    :rtype: bool
    """

    if ismethod(elt):
        elt = elt.__func__

    result = hasattr(elt, __PROXIFIED__)

    return result
