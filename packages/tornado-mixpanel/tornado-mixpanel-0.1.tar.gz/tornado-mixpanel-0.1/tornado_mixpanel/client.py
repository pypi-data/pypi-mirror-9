#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Asumi Kamikaze Inc.
# Licensed under the MIT License.
# Author: Alejandro M. Bernardis
# Email: alejandro (dot) bernardis (at) asumikamikaze (dot) com
# Created: 03/Feb/2015 13:02

import time
from . import _compat, MIXPANEL_EVENTS, MIXPANEL_PEOPLE
from .consumer import MixpanelConsumer, MixpanelBufferedConsumer
from .utils import dispatch
from tornado import gen


class ClientError(Exception):
    pass


class AsyncMixpanelClient(object):
    VERSION = '1.0.0'
    VERSION_NAME = 'python/tornado'

    def __init__(self, token, buffered=False, **settings):
        if not isinstance(token, _compat.string_types) or not len(token):
            raise ClientError('Token not found')
        self._token = token
        if not buffered:
            self._consumer = MixpanelConsumer(**settings)
        else:
            self._consumer = MixpanelBufferedConsumer(**settings)

    @property
    def consumer(self):
        return self._consumer

    def _sanitize_argument(self, value, default):
        return default if value is None else value

    @gen.coroutine
    def import_data(self, api_key, distinct_id, event_name, timestamp,
                    properties=None, meta=None, callback=None):
        prop = {
            'token': self._token,
            'distinct_id': distinct_id,
            'time': int(timestamp),
            'mp_lib': self.VERSION_NAME,
            '$lib_version': self.VERSION,
        }
        prop.update(self._sanitize_argument(properties, {}))
        data = {'event': event_name, 'properties': prop}
        data.update(self._sanitize_argument(meta, {}))
        response = yield self._consumer.send(MIXPANEL_EVENTS, data,
                                             api_key=api_key)
        dispatch(response, callback)

    @gen.coroutine
    def track(self, distinct_id, event_name, properties=None, meta=None,
              callback=None):
        prop = {
            'token': self._token,
            'distinct_id': distinct_id,
            'time': int(time.time()),
            'mp_lib': self.VERSION_NAME,
            '$lib_version': self.VERSION,
        }
        prop.update(self._sanitize_argument(properties, {}))
        data = {'event': event_name, 'properties': prop}
        data.update(self._sanitize_argument(meta, {}))
        response = yield self._consumer.send(MIXPANEL_EVENTS, data)
        dispatch(response, callback)

    @gen.coroutine
    def alias(self, alias_id, original, meta=None, callback=None):
        data = {
            'event': '$create_alias',
            'properties': {
                'distinct_id': original,
                'alias': alias_id,
                'token': self._token
            }
        }
        data.update(self._sanitize_argument(meta, {}))
        response = yield self._consumer.fetch(MIXPANEL_EVENTS, data)
        dispatch(response, callback)

    @gen.coroutine
    def people(self, distinct_id, message, meta=None, callback=None):
        data = {
            '$token': self._token,
            '$distinct_id': distinct_id,
            '$time': int(time.time() * 1000)
        }
        data.update(message, **self._sanitize_argument(meta, {}))
        response = yield self._consumer.send(MIXPANEL_PEOPLE, data)
        dispatch(response, callback)

    def people_set(self, distinct_id, properties, meta=None, callback=None):
        return self.people(distinct_id, {'$set': properties}, meta, callback)

    def people_set_once(self, distinct_id, properties, meta=None,
                        callback=None):
        return self.people(distinct_id, {'$set_once': properties}, meta,
                           callback)

    def people_add(self, distinct_id, properties, meta=None, callback=None):
        return self.people(distinct_id, {'$add': properties}, meta, callback)

    def people_append(self, distinct_id, properties, meta=None, callback=None):
        return self.people(distinct_id, {'$append': properties}, meta, callback)

    def people_union(self, distinct_id, properties, meta=None, callback=None):
        return self.people(distinct_id, {'$union': properties}, meta, callback)

    def people_unset(self, distinct_id, properties, meta=None, callback=None):
        return self.people(distinct_id, {'$unset': properties}, meta, callback)

    def people_delete(self, distinct_id, meta=None, callback=None):
        return self.people(distinct_id, {'$delete': ''}, meta, callback)

    def people_track_charge(self, distinct_id, amount, properties=None,
                            meta=None, callback=None):
        properties = self._sanitize_argument(properties, {})
        properties['$amount'] = amount
        return self.people_append(distinct_id, {'$transactions': properties},
                                  meta, callback)

    def people_clear_charges(self, distinct_id, meta=None, callback=None):
        return self.people_unset(distinct_id, ["$transactions"], meta, callback)
