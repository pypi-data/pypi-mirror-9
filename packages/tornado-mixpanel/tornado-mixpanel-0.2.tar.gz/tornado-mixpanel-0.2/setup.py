#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Asumi Kamikaze Inc.
# Licensed under the MIT License.
# Author: Alejandro M. Bernardis
# Email: alejandro (dot) bernardis (at) asumikamikaze (dot) com
# Created: 02/Feb/2015 14:01

from tornado_mixpanel import version
from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='tornado-mixpanel',
    version=version,
    url='https://github.com/alejandrobernardis/tornado-mixpanel',
    license='MIT',
    author='Alejandro M. Bernardis',
    author_email='alejandro.m.bernardis@gmail.com',
    description='An async client for mixpanel.',
    long_description=readme,
    classifiers=[
        'Development Status :: 4 - Beta',
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
