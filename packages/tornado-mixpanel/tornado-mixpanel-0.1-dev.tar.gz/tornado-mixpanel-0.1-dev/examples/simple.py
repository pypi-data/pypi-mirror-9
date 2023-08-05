#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Asumi Kamikaze Inc.
# Licensed under the MIT License.
# Author: Alejandro M. Bernardis
# Email: alejandro (dot) bernardis (at) asumikamikaze (dot) com
# Created: 03/Feb/2015 13:57

from tornado import gen, ioloop
from tornado_mixpanel.client import AsyncMixpanelClient


@gen.coroutine
def run():
    client = AsyncMixpanelClient('<mixpanel-token>')
    raw_input('Press (enter) to continue...')

    try:
        r = yield client.track(
            'user-xxxx', 'steps', {'step_one': True, 'step_two': False})
        print r.body

        r = yield client.people_set(
            'client-xxxx', {'fullname': 'Alejandro Bernardis'})
        print r.body

        r = yield client.people_append(
            'client-xxxx', {'age': 31, 'locale': 'es_AR'})
        print r.body
    except Exception, e:
        print e

    ioloop.IOLoop.current().stop()


if __name__ == '__main__':
    run()
    ioloop.IOLoop.instance().start()