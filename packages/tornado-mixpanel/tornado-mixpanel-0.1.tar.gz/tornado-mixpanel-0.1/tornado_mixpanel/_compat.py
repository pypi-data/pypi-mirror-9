#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Asumi Kamikaze Inc.
# Licensed under the MIT License.
# Author: Alejandro M. Bernardis
# Email: alejandro (dot) bernardis (at) asumikamikaze (dot) com
# Created: 03/Feb/2015 13:07

# TODO(berna): Support for Python 3.0+

import datetime

try:
    import ujson as json
except ImportError:
    try:
        import ujson as json
    except ImportError:
        import json


string_types = basestring
list_types = (tuple, list)

primitive_types = \
    (complex, int, float, long, bool, str, basestring, unicode, tuple, list)

datetime_types = \
    (datetime.date, datetime.time, datetime.datetime, datetime.timedelta)
