#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Asumi Kamikaze Inc.
# Licensed under the MIT License.
# Author: Alejandro M. Bernardis
# Email: alejandro (dot) bernardis (at) asumikamikaze (dot) com
# Created: 03/Feb/2015 13:57

import time
from tornado import gen, ioloop
from tornado_mixpanel.client import AsyncMixpanelClient


@gen.coroutine
def run():
    client = AsyncMixpanelClient('<mixpanel-token>', True)
    raw_input('Press (enter) to continue...')

    try:
        username = int(time.time())

        for i in xrange(10):
            print i,
            yield client.track(username, 'item_%s' % i, {'i': i})
            time.sleep(1)

        print '\n' * 2
        print '-*-' * 80

        r = yield client.consumer.flush()
        print r

    except Exception, e:
        print e

    ioloop.IOLoop.current().stop()


if __name__ == '__main__':
    run()
    ioloop.IOLoop.instance().start()