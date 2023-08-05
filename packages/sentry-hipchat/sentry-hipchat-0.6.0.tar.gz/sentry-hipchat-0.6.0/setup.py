#!/usr/bin/env python
"""
sentry-hipchat
==============

An extension for Sentry which integrates with Hipchat. It will forwards
notifications to an hipchat room.

:copyright: (c) 2011 by the Linovia, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages


tests_require = [
    'pytest',
    'mock',
]

install_requires = [
    'sentry>=6.0.0',
]

setup(
    name='sentry-hipchat',
    version='0.6.0',
    author='Xavier Ordoquy',
    author_email='xordoquy@linovia.com',
    url='http://github.com/linovia/sentry-hipchat',
    description='A Sentry extension which integrates with Hipchat.',
    long_description=__doc__,
    license='BSD',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    include_package_data=True,
    entry_points={
        'sentry.apps': [
            'sentry_hipchat = sentry_hipchat ',
        ],
        'sentry.plugins': [
            'hipchat = sentry_hipchat.models:HipchatMessage',
         ],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
