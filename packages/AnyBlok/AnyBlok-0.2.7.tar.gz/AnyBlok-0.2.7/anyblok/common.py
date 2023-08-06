# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import sys
from functools import lru_cache


def format_bloks(bloks):
    if bloks == '':
        bloks = None

    if bloks is not None:
        bloks = bloks.split(',')

    return bloks


def function_name(function):
    if sys.version_info < (3, 3):
        return function.__name__
    else:
        return function.__qualname__


def python_version():
    vi = sys.version_info
    return (vi.major, vi.minor)


class TypeList(list):

    def __init__(self, Model, registry, namespace,
                 transformation_properties=None):
        super(TypeList, self).__init__()
        self.Model = Model
        self.registry = registry
        self.namespace = namespace
        self.transformation_properties = transformation_properties

    def transform_base(self, base, namespace=None):
        if base in self.registry.removed:
            return None

        if namespace is None:
            namespace = self.namespace

        newbase = self.Model.transform_base(
            self.registry, namespace, base, self.transformation_properties)
        return newbase

    def append(self, base, **kwargs):
        newbase = self.transform_base(base, **kwargs)
        if newbase:
            super(TypeList, self).append(newbase)

    def extend(self, bases, **kwargs):
        newbases = [x
                    for y in bases
                    for x in [self.transform_base(y, **kwargs)]
                    if x is not None]
        if newbases:
            super(TypeList, self).extend(newbases)


def apply_cache(registry, namespace, base, properties):
    """ Find the cached methods in the base to apply the real cache
    decorator

    :param registry: the current  registry
    :param namespace: the namespace of the model
    :param base: One of the base of the model
    :param properties: the properties of the model
    :rtype: new base
    """
    methods_cached = {}

    def apply_wrapper(attr, method):
        @lru_cache(maxsize=method.size)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)

        wrapper.indentify = (namespace, attr)
        registry.caches[namespace][attr].append(wrapper)
        if method.is_cache_classmethod:
            methods_cached[attr] = classmethod(wrapper)
        else:
            methods_cached[attr] = wrapper

    for attr in dir(base):
        method = getattr(base, attr)
        if not hasattr(method, 'is_cache_method'):
            continue
        elif method.is_cache_method is True:
            if namespace not in registry.caches:
                registry.caches[namespace] = {attr: []}
            elif attr not in registry.caches[namespace]:
                registry.caches[namespace][attr] = []

            apply_wrapper(attr, method)

    if methods_cached:
        return type(namespace, (base,), methods_cached)

    return base
