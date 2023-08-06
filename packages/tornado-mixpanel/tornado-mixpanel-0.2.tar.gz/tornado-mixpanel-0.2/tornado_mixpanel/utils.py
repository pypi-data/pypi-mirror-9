#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Asumi Kamikaze Inc.
# Licensed under the MIT License.
# Author: Alejandro M. Bernardis
# Email: alejandro (dot) bernardis (at) asumikamikaze (dot) com
# Created: 03/Feb/2015 13:03

from . import _compat
from tornado import gen


# Decorators

def value_or_none(func):
    def decorator(value, *args, **kwargs):
        if value is None:
            return None
        return func(value, *args, **kwargs)
    return decorator


def string_or_error(func):
    def decorator(value, *args, **kwargs):
        if not isinstance(value, _compat.string_types):
            raise TypeError('Must be a string type.')
        return func(value, *args, **kwargs)
    return decorator


def dict_or_error(func):
    def decorator(value, *args, **kwargs):
        if not isinstance(value, dict):
            raise TypeError('Must be a dict type.')
        return func(value, *args, **kwargs)
    return decorator


# Strings

@string_or_error
def want_bytes(value, encoding='utf-8', errors='strict'):
    if isinstance(value, _compat.unicode_types):
        value = value.encode(encoding, errors)
    return value


# Dictionary

@dict_or_error
def setdefault(source, key, default):
    source[key] = source.get(key, None) or default


# Async

def dispatch(response, callback=None):
    if callback is None:
        raise gen.Return(response)
    callback(response)


# Misc

@value_or_none
def complex_types(value):
    if isinstance(value, _compat.unicode_types):
        return want_bytes(value)
    elif isinstance(value, _compat.primitive_types):
        return value
    elif isinstance(value, _compat.datetime_types):
        return value.isoformat()
    return _compat.bytes_types(value)