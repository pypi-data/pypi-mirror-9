#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Asumi Kamikaze Inc.
# Licensed under the MIT License.
# Author: Alejandro M. Bernardis
# Email: alejandro (dot) bernardis (at) asumikamikaze (dot) com
# Created: 03/Feb/2015 13:02

import base64
from . import _compat, MIXPANEL_ENDPOINTS_KEYS, \
    MIXPANEL_ENDPOINTS
from .utils import setdefault, complex_types, want_bytes, \
    dispatch
from collections import deque
from datetime import datetime, timedelta
from functools import wraps
from tornado import gen
from tornado.httpclient import HTTPRequest, HTTPResponse, AsyncHTTPClient, \
    HTTPError
from urllib import urlencode


class ConsumerError(Exception):
    pass


def is_endpoint(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        endpoint = kwargs.get('endpoint', args[0])
        if endpoint not in MIXPANEL_ENDPOINTS_KEYS:
            raise gen.Return(ConsumerError(
                'No such endpoints "%s". Valid endpoints are one of %s.'
                % (endpoint, MIXPANEL_ENDPOINTS_KEYS)))
        return method(self, *args, **kwargs)
    return wrapper


def is_buffered(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, '_buffered', False):
            raise gen.Return(ConsumerError(
                'Async buffered consumer not supported'))
        return method(self, *args, **kwargs)
    return wrapper


class MixpanelConsumer(object):
    def __init__(self, endpoints=None, **settings):
        AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')
        for item in settings.get('endpoints', endpoints or {}).keys():
            if item not in MIXPANEL_ENDPOINTS_KEYS:
                raise ConsumerError('Endpoint not supported: %s' % item)
        setdefault(settings, 'endpoints', MIXPANEL_ENDPOINTS)
        self._endpoints = settings['endpoints']

    def _sanitize_message(self, message):
        if isinstance(message, deque):
            message = list(message)
        return _compat.json\
            .dumps(message, default=complex_types, separators=(',', ':'))

    def _sanitize_body(self, message, api_key=None):
        if isinstance(message, (deque, list, tuple, dict)):
            message = self._sanitize_message(message)
        elif not isinstance(message, _compat.string_types):
            raise ConsumerError('Invalid message, must be a string')
        message = base64.b64encode(want_bytes(message))
        values = {'data': message, 'verbose': 1, 'ip': 0}
        if api_key is not None:
            values['api_key'] = api_key
        return urlencode(values, True).encode('utf-8')

    def _sanitize_headers(self, headers=None):
        return headers

    def _sanitize_response(self, response=None, error=None):
        if isinstance(error, HTTPError):
            response = error.response
        if not isinstance(response, HTTPResponse):
            raise ConsumerError('Response must be a '
                                '"tornado.httpclient.HTTPResponse".')
        body = _compat.json.loads(response.body)
        if response.code != 200 or response.error or body.get('status', 0) != 1:
            raise ConsumerError(body, response)
        return body

    @gen.coroutine
    @is_endpoint
    def fetch(self, endpoint, message, headers=None, **kwargs):
        try:
            request = HTTPRequest(self._endpoints[endpoint], 'POST')
            request.headers = self._sanitize_headers(headers)
            request.body = self._sanitize_body(message)
            for key, value in kwargs.items():
                setattr(request, key, value)
            try:
                response = yield AsyncHTTPClient().fetch(request)
                response = self._sanitize_response(response)
            except HTTPError, e:
                response = self._sanitize_response(error=e)
            except Exception, e:
                response = e
        except Exception, e:
            response = ConsumerError(e.message)
        raise gen.Return(response)

    @gen.coroutine
    @is_endpoint
    def send(self, endpoint, message, callback=None, **kwargs):
        try:
            response = yield self.fetch(endpoint, message, **kwargs)
        except ConsumerError, e:
            response = e
        except Exception, e:
            response = ConsumerError(None, e)
        dispatch(response, callback)


class MixpanelBufferedConsumer(MixpanelConsumer):
    ALL = 'all'
    ENDPOINT = 'endpoint'

    def __init__(self, endpoints=None, flush_after=60, flush_first=True,
                 max_size=50, **kwargs):
        self._current = {key: deque() for key in MIXPANEL_ENDPOINTS_KEYS}
        self._buffers = {key: deque() for key in MIXPANEL_ENDPOINTS_KEYS}
        self._flush_first = flush_first
        self._flush_after = timedelta(0, flush_after)
        self._last_flushed = None if not flush_after else datetime.utcnow()
        self._errors = None
        self._max_size = min(max_size, 50)
        super(MixpanelBufferedConsumer, self).__init__(endpoints, **kwargs)

    @property
    def errors(self):
        return self._errors

    def _should_flush(self, endpoint=None):
        full = endpoint and len(self._current[endpoint]) >= self._max_size
        stale = self._last_flushed is None
        if not stale and self._flush_after:
            stale = datetime.utcnow() - self._last_flushed > self._flush_after
        if stale:
            return self.ALL
        if full:
            return self.ENDPOINT
        return False

    @gen.coroutine
    def _prepare_flush(self, endpoint=None, **kwargs):
        errors = []
        endpoints = [endpoint] if endpoint in MIXPANEL_ENDPOINTS_KEYS \
            else MIXPANEL_ENDPOINTS_KEYS
        for endpoint in endpoints:
            current = self._current[endpoint]
            if not len(current):
                continue
            buffering = self._buffers[endpoint]
            buffering.extend(current)
            current.clear()
            try:
                # TODO(berna): collect and analyze results
                message = '[{0}]'.format(','.join(buffering))
                yield self.fetch(endpoint, message, **kwargs)
            except Exception, e:
                current.extendleft(buffering)
                errors.append(ConsumerError(endpoint, e))
            buffering.clear()
        response = len(errors) == 0
        self._errors = None if response else errors
        raise gen.Return(response)

    @gen.coroutine
    def flush(self, callback=None, **kwargs):
        response = yield self._prepare_flush(**kwargs)
        dispatch(response, callback)

    @gen.coroutine
    @is_endpoint
    def send(self, endpoint, message, callback=None, **kwargs):
        response = False
        current = self._current[endpoint]
        current.append(self._sanitize_message(message))
        try:
            should = self._should_flush(endpoint)
        except:
            should = False
        if should == self.ALL:
            response = yield self._prepare_flush(**kwargs)
        elif should == self.ENDPOINT:
            response = yield self._prepare_flush(endpoint, **kwargs)
        dispatch(response, callback)
