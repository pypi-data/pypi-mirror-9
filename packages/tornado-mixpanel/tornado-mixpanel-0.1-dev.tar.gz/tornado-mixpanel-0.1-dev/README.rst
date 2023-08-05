Tornado Mixpanel
================

Tornado Mixpanel is an async library for Mixpanel service. This library allows 
for server-side integration of Mixpanel.


Installation
------------

**Automatic installation**:

    pip install tornado-mixpanel   

Tornado Mixpanel is listed in `PyPI <http://pypi.python.org/pypi/
tornado-mixpanel/>`_ and can be installed with ``pip`` or ``easy_install``.

**Manual installation**: Download the latest source from `PyPI <http://pypi.
python.org/pypi/tornado-mixpanel/>`_.

.. parsed-literal::

    tar xvzf tornado-mixpanel-$VERSION.tar.gz
    cd tornado-mixpanel-$VERSION
    python setup.py build
    sudo python setup.py install

The Tornado Mixpanel source code is `hosted on GitHub <https://github.com/
alejandrobernardis/tornado-mixpanel>`_.


Example
-------

Here is a simple example:

.. code-block:: python

    #!/usr/bin/env python2.7
    # -*- coding: utf-8 -*-
    
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


License
-------

The MIT License (MIT)

Copyright (c) 2015 Alejandro Bernardis and contributors.  See AUTHORS
for more details.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
