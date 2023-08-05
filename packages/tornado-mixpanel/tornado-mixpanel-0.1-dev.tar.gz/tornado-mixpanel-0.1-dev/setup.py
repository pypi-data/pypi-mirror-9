#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Asumi Kamikaze Inc.
# Licensed under the MIT License.
# Author: Alejandro M. Bernardis
# Email: alejandro (dot) bernardis (at) asumikamikaze (dot) com
# Created: 02/Feb/2015 14:01

"""
Tornado Mixpanel
----------------

Tornado Mixpanel is an async library for Mixpanel service. This library allows
for server-side integration of Mixpanel.


Example
```````

.. code:: python
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


Easy to Setup
`````````````

.. code:: bash
    $ pip install tornado-mixpanel


Links
`````

* `website <https://github.com/alejandrobernardis/tornado-mixpanel>`_

"""

from tornado_mixpanel import version
from setuptools import setup, find_packages


setup(
    name='tornado-mixpanel',
    version=version,
    url='https://github.com/alejandrobernardis/tornado-mixpanel',
    license='MIT',
    author='Alejandro M. Bernardis',
    author_email='alejandro.m.bernardis@gmail.com',
    description='An async client for mixpanel.',
    long_description=__doc__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Natural Language :: Spanish',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    packages=find_packages(exclude=['docs', 'examples', 'scripts', 'templates',
                                    'tests', 'libs']),
    package_data={'': ['CHANGES', 'LICENSE', 'AUTHORS', 'README.rst']},
    package_dir={'tornado_mixpanel': 'tornado_mixpanel'},
    include_package_data=True,
    zip_safe=False,
    platforms=['Linux'],
    install_requires=[line.strip() for line in open('requirements.txt', 'r')]
)
