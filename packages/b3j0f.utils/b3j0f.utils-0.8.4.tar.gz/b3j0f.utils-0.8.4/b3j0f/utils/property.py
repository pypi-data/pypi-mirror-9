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
Library which aims to bind named properties on any element at runtime.

This module can bind a named property on any element but None methods.

In preserving binding from inheritance and automatical mechanisms which prevent
to set any attribute on any elements.

When you are looking for an element bound property, the result is a dictionary
of the shape {element, {property name, property}}.

.. warning:

    - It is adviced to delete properties from cache after deleting them at
        runtime in order to avoid memory leak.
"""

__all__ = [
    'get_properties',
    'get_first_property', 'get_first_properties',
    'get_local_property', 'get_local_properties',
    'put_properties', 'del_properties',
    'firsts', 'remove_ctx',
    'setdefault', 'free_cache',
    'find_ctx'
]

from b3j0f.utils.version import PY2
from b3j0f.utils.iterable import ensureiterable

from inspect import ismethod

from collections import Hashable

try:
    from threading import Timer
except ImportError:
    from dummy_threading import Timer

__B3J0F__PROPERTIES__ = '__b3j0f_props'  #: __dict__ properties key

__DICT__ = '__dict__'  #: __dict__ elt attribute name
__CLASS__ = '__class__'  #: __class__ elt attribute name
__SELF__ = '__self__'  #: __self__ class instance attribute name
__BASES__ = '__bases__'  # __bases__ class attribute name

__STATIC_ELEMENTS_CACHE__ = {}  #: dictionary of properties for static objects
__UNHASHABLE_ELTS_CACHE__ = {}  #: dictionary of properties for unhashable obj


def find_ctx(elt):
    """
    Get the right ctx related to input elt.

    In order to keep safe memory as much as possible, it is important to find
    the right context element. For example, instead of putting properties on
    a function at the level of an instance, it is important to save such
    property on the instance because the function.__dict__ is shared with
    instance class function, and so, if the instance is deleted from memory,
    the property is still present in the class memory. And so on, it is
    impossible to identify the right context in such case if all properties
    are saved with the same key in the same function which is the function.
    """

    result = elt  # by default, result is ctx

    # if elt is ctx and elt is a method, it is possible to find the best ctx
    if ismethod(elt):
        # get instance and class of the elt
        instance = elt.__self__
        # if instance is not None, the right context is the instance
        if instance is not None:
            result = instance

        elif PY2:
            result = elt.im_class

    return result


def free_cache(ctx, *elts):
    """
    Free properties bound to input cached elts. If empty, free the whole cache.
    """

    global __STATIC_ELEMENTS_CACHE__, __UNHASHABLE_ELTS_CACHE__

    for elt in elts:
        if isinstance(elt, Hashable):
            cache = __STATIC_ELEMENTS_CACHE__
        else:
            cache = __UNHASHABLE_ELTS_CACHE__
            elt = id(elt)
        if elt in cache:
            del cache[elt]

    if not elts:
        __STATIC_ELEMENTS_CACHE__ = {}
        __UNHASHABLE_ELTS_CACHE__ = {}


def _ctx_elt_properties(elt, ctx=None, create=False):
    """
    Get elt properties related to a ctx.

    :param elt: property component elt. Not None methods or unhashable types.
    :param ctx: elt ctx from where get properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.
    :param bool create: create ctx elt properties if not exist.

    :return: dictionary of property by name embedded into ctx __dict__ or in
        shared __STATIC_ELEMENTS_CACHE__ or else in shared
        __UNHASHABLE_ELTS_CACHE__. None if no properties exists.
    :rtype: dict
    """

    result = None

    if ctx is None:
        ctx = find_ctx(elt=elt)

    ctx_properties = None

    # in case of dynamic object, parse the ctx __dict__
    ctx__dict__ = getattr(ctx, __DICT__, None)
    if ctx__dict__ is not None and isinstance(ctx__dict__, dict):
        # if properties exist in ctx__dict__
        if __B3J0F__PROPERTIES__ in ctx__dict__:
            ctx_properties = ctx__dict__[__B3J0F__PROPERTIES__]
        elif create:  # if create in worst case
            ctx_properties = ctx__dict__[__B3J0F__PROPERTIES__] = {}

    else:  # in case of static object
        if isinstance(ctx, Hashable):  # search among static elements
            cache = __STATIC_ELEMENTS_CACHE__
        else:  # or unhashable elements
            cache = __UNHASHABLE_ELTS_CACHE__
            ctx = id(ctx)
            if not isinstance(elt, Hashable):
                elt = id(elt)
        # if ctx is in cache
        if ctx in cache:
            # get its properties
            ctx_properties = cache[ctx]
        elif create:  # elif create, get an empty dict
            ctx_properties = cache[ctx] = {}

    # if ctx_properties is not None
    if ctx_properties is not None:
        # check if elt exist in ctx_properties
        if elt in ctx_properties:
            result = ctx_properties[elt]
        elif create:  # create the right data if create
            if create:
                result = ctx_properties[elt] = {}

    return result


def get_properties(elt, keys=None, ctx=None):
    """
    Get elt properties.

    :param elt: properties elt. Not None methods or unhashable types.
    :param keys: key(s) of properties to get from elt.
        If None, get all properties.
    :type keys: list or str
    :param ctx: elt ctx from where get properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.

    :return: list of properties by elt and name.
    :rtype: list
    """

    # initialize keys if str
    if isinstance(keys, str):
        keys = (keys,)

    result = _get_properties(elt, keys=keys, local=False, ctx=ctx)

    return result


def get_property(elt, key, ctx=None):
    """
    Get elt key property.

    :param elt: property elt. Not None methods.
    :param key: property key to get from elt.
    :param ctx: elt ctx from where get properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.

    :return: list of property values by elt.
    :rtype: list
    """

    result = []

    properties = get_properties(elt=elt, ctx=ctx, keys=key)

    if key in properties:
        result = properties[key]

    return result


def get_first_properties(elt, keys=None, ctx=None):
    """
    Get first properties related to one input key

    :param elt: first property elt. Not None methods.
    :param list keys: property keys to get.
    :param ctx: elt ctx from where get properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.

    :return: dict of first values of elt properties.
    """

    # ensure keys is an iterable if not None
    if isinstance(keys, str):
        keys = (keys,)

    result = _get_properties(elt, keys=keys, first=True, ctx=ctx)

    return result


def get_first_property(elt, key, default=None, ctx=None):
    """
    Get first property related to one input key

    :param elt: first property elt. Not None methods.
    :param str key: property key to get.
    :param default: default value to return if key does not exist in elt.
        properties
    :param ctx: elt ctx from where get properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.
    """

    result = default

    properties = _get_properties(elt, keys=(key,), ctx=ctx, first=True)

    # set value if key exists in properties
    if key in properties:
        result = properties[key]

    return result


def get_local_properties(elt, keys=None, ctx=None):
    """
    Get local elt properties (not defined in elt type or base classes).

    :param elt: local properties elt. Not None methods.
    :param keys: keys of properties to get from elt.
    :param ctx: elt ctx from where get properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.

    :return: dict of properties by name.
    :rtype: dict
    """

    if isinstance(keys, str):
        keys = (keys,)

    result = _get_properties(elt, keys=keys, local=True, ctx=ctx)

    return result


def get_local_property(elt, key, default=None, ctx=None):
    """
    Get one local property related to one input key or default value if key is
        not found.

    :param elt: local property elt. Not None methods.
    :param str key: property key to get.
    :param default: default value to return if key does not exist in elt
        properties.
    :param ctx: elt ctx from where get properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.
    :return: dict of properties by name.
    :rtype: dict
    """

    result = default

    local_properties = get_local_properties(elt=elt, keys=(key,), ctx=ctx)

    if key in local_properties:
        result = local_properties[key]

    return result


def _get_properties(
    elt, keys=None, local=False, exclude=None, first=False, ctx=None,
    _found_keys=None
):
    """
    Get a dictionary of elt properties.

    Such dictionary is filled related to the elt properties, and from all base
        elts properties if not local.

    :param elt: properties elt. Not None methods.
    :param ctx: elt ctx from where get properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.
    :param keys: keys of properties to get from elt. If None, get all
        properties.
    :param bool local: if False, get properties from bases classes and type
        as well.
    :param set exclude: elts from where not get properties.
    :param bool first: get only first property values.
    :param _found_keys: used such as a cache value for result.

    :return: dict of properties by name and ...:

        - if local or first: value.
        - other cases: [(elt, value)] in order of property definition even if
            multi inheritance do not ensure to respect inheritance order in a
            list.
    :rtype: dict
    """

    result = {}

    # get the best context
    if ctx is None:
        ctx = find_ctx(elt=elt)

    # initialize found keys
    if first and _found_keys is None:
        _found_keys = set()

    # get elt properties if exist
    elt_properties = _ctx_elt_properties(elt=elt, ctx=ctx, create=False)

    # if elt_properties exists
    if elt_properties is not None:
        # if elt properties is not empty
        # try to add property values in result related to input keys
        properties_to_keep = elt_properties.copy() if keys is None else {}
        # get key values
        if keys is not None:
            for key in keys:
                if key in elt_properties:
                    if not first or key not in _found_keys:
                        properties_to_keep[key] = elt_properties[key]
                    if first and not key in _found_keys:
                        _found_keys.add(key)

        if local:  # in case of local, use properties_to_keep
            result = properties_to_keep

        # if not local and not first and properties to keep
        elif not first and properties_to_keep:
            for name in properties_to_keep:
                property_to_keep = properties_to_keep[name]
                # add (elt, properties_to_keep) in result
                if name not in result:
                    result[name] = [(elt, property_to_keep)]
                else:
                    result[name].append((elt, property_to_keep))

        # in case of first, result is properties_to_keep
        elif properties_to_keep:
            result = properties_to_keep
    # check if all keys have been found if first
    keys_left = not first or keys is None or len(keys) != len(_found_keys)

    # if not local or keys left
    if not local and keys_left:
        # initialize exclude
        if exclude is None:
            exclude = set()

        # add elt in exclude in order to avoid to get elt properties twice
        if isinstance(elt, Hashable):
            exclude.add(elt)

        # and search among bases ctx elements
        if ctx is not elt:
            # go to base elts
            try:
                elt_name = elt.__name__
            except AttributeError:
                pass
            else:
                # if elt is a sub attr of ctx
                if hasattr(ctx, elt_name):
                    if hasattr(ctx, __BASES__):
                        ctx_bases = ctx.__bases__
                    elif hasattr(ctx, __CLASS__):
                        ctx_bases = (ctx.__class__,)
                    else:
                        ctx_bases = ()
                    for base_ctx in ctx_bases:
                        # get base_elt properties
                        base_elt = getattr(base_ctx, elt_name, None)
                        if base_elt is not None:
                            base_properties = _get_properties(
                                elt=base_elt,
                                keys=keys,
                                local=local,
                                exclude=exclude,
                                ctx=base_ctx,
                                _found_keys=_found_keys
                            )
                            # update result with base_properties
                            for name in base_properties:
                                properties = base_properties[name]
                                if name not in result:
                                    result[name] = properties
                                else:
                                    result[name] += properties

        else:
            # bases classes
            if hasattr(elt, __BASES__):
                for base in elt.__bases__:
                    if base not in exclude:
                        base_result = _get_properties(
                            elt=base,
                            keys=keys,
                            local=local,
                            exclude=exclude,
                            ctx=base,
                            _found_keys=_found_keys
                        )
                        # update result with base_result
                        for name in base_result:
                            properties = base_result[name]
                            if name not in result:
                                result[name] = properties
                            else:
                                result[name] += properties

            # search among type definition

            # class
            if hasattr(elt, __CLASS__):
                elt_class = elt.__class__
                # get class properties only if elt is not its own class
                if elt_class is not elt and elt_class not in exclude:
                    elt_class_properties = _get_properties(
                        elt=elt_class,
                        keys=keys,
                        local=local,
                        exclude=exclude,
                        ctx=elt_class,
                        _found_keys=_found_keys
                    )
                    # update result with class result
                    for name in elt_class_properties:
                        properties = elt_class_properties[name]
                        if name not in result:
                            result[name] = properties
                        else:
                            result[name] += properties

            # type
            elt_type = type(elt)
            # get elt type properties only if elt is not its type
            if elt_type is not elt and elt_type not in exclude:
                elt_type_properties = _get_properties(
                    elt=elt_type,
                    keys=keys,
                    local=local,
                    exclude=exclude,
                    ctx=elt_type,
                    _found_keys=_found_keys
                )
                # update result with type properties
                for name in elt_type_properties:
                    properties = elt_type_properties[name]
                    if name not in result:
                        result[name] = properties
                    else:
                        result[name] += properties

    return result


def put_property(elt, key, value, ttl=None, ctx=None):
    """Put properties in elt.

    :param elt: properties elt to put. Not None methods.
    :param number ttl: If not None, property time to leave.
    :param ctx: elt ctx from where put properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.
    :param dict properties: properties to put in elt. elt and ttl are exclude.

    :return: Timer if ttl is not None.
    :rtype: Timer
    """
    return put_properties(elt=elt, properties={key: value}, ttl=ttl, ctx=ctx)


def put_properties(elt, properties, ttl=None, ctx=None):
    """Put properties in elt.

    :param elt: properties elt to put. Not None methods.
    :param number ttl: If not None, property time to leave.
    :param ctx: elt ctx from where put properties. Equals elt if None. It
        allows to get function properties related to a class or instance if
        related function is defined in base class.
    :param dict properties: properties to put in elt. elt and ttl are exclude.

    :return: Timer if ttl is not None.
    :rtype: Timer
    """

    result = None

    if properties:

        # get the best context
        if ctx is None:
            ctx = find_ctx(elt=elt)

        # get elt properties
        elt_properties = _ctx_elt_properties(elt=elt, ctx=ctx, create=True)

        # set properties
        elt_properties.update(properties)

        if ttl is not None:
            kwargs = {
                'elt': elt,
                'ctx': ctx,
                'keys': tuple(properties.keys())
            }
            result = Timer(ttl, del_properties, kwargs=kwargs)
            result.start()

    return result


def put(properties, ttl=None, ctx=None):
    """
    Decorator dedicated to put properties on an element.
    """

    def put_on(elt):
        return put_properties(elt=elt, properties=properties, ttl=ttl, ctx=ctx)

    return put_on


def del_properties(elt, keys=None, ctx=None):
    """
    Delete elt property.

    :param elt: properties elt to del. Not None methods.
    :param keys: property keys to delete from elt. If empty, delete all
        properties.
    """

    # get the best context
    if ctx is None:
        ctx = find_ctx(elt=elt)

    elt_properties = _ctx_elt_properties(elt=elt, ctx=ctx, create=False)

    # if elt properties exist
    if elt_properties is not None:

        if keys is None:
            keys = list(elt_properties.keys())

        else:
            keys = ensureiterable(keys, iterable=tuple, exclude=str)

        for key in keys:
            if key in elt_properties:
                del elt_properties[key]

        # delete property component if empty
        if not elt_properties:
            # case of dynamic object
            if isinstance(getattr(ctx, '__dict__', None), dict):
                try:
                    if elt in ctx.__dict__[__B3J0F__PROPERTIES__]:
                        del ctx.__dict__[__B3J0F__PROPERTIES__][elt]
                except TypeError:  # if elt is unhashable
                    elt = id(elt)
                    if elt in ctx.__dict__[__B3J0F__PROPERTIES__]:
                        del ctx.__dict__[__B3J0F__PROPERTIES__][elt]
                # if ctx_properties is empty, delete it
                if not ctx.__dict__[__B3J0F__PROPERTIES__]:
                    del ctx.__dict__[__B3J0F__PROPERTIES__]

            # case of static object and hashable
            else:
                if isinstance(ctx, Hashable):
                    cache = __STATIC_ELEMENTS_CACHE__
                else:  # case of static and unhashable object
                    cache = __UNHASHABLE_ELTS_CACHE__
                    ctx = id(ctx)
                    if not isinstance(elt, Hashable):
                        elt = id(elt)

                # in case of static object
                if ctx in cache:
                    del cache[ctx][elt]
                    if not cache[ctx]:
                        del cache[ctx]


def firsts(properties):
    """
    Transform a dictionary of {name: [(elt, value)+]} (resulting from
        get_properties) to a dictionary of {name, value} where names are first
        encountered in input properties.

    :param dict properties: properties to firsts.
    :return: dictionary of parameter values by names.
    :rtype: dict
    """

    result = {}

    # parse elts
    for name in properties:
        elt_properties = properties[name]
        # add property values in result[name]
        result[name] = elt_properties[0][1]

    return result


def remove_ctx(properties):
    """
    Transform a dictionary of {name: [(elt, value)+]} into a dictionary of
        {name: [value+]}.

    :param dict properties: properties from where get only values.
    :return: dictionary of parameter values by names.
    :rtype: dict
    """
    result = {}

    for name in properties:
        elt_properties = properties[name]
        result[name] = []
        for _, value in elt_properties:
            result[name].append(value)

    return result


def setdefault(elt, key, default, ctx=None):
    """
    Get a local property and create default value if local property does not
        exist.

    :param elt: local proprety elt to get/create. Not None methods.
    :param str key: proprety name.
    :param default: property value to set if key no in local properties.

    :return: property value or default if property does not exist.
    """

    result = default

    # get the best context
    if ctx is None:
        ctx = find_ctx(elt=elt)

    # get elt properties
    elt_properties = _ctx_elt_properties(elt=elt, ctx=ctx, create=True)

    # if key exists in elt properties
    if key in elt_properties:
        # result is elt_properties[key]
        result = elt_properties[key]
    else:  # set default property value
        elt_properties[key] = default

    return result
