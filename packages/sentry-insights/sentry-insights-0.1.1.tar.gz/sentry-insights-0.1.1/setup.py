#!/usr/bin/env python
"""
sentry-insights
===============

An extension for Sentry which integrates with Insights.
It will send issues notification to Insights with every tag.
It's based on sentry-hipchat plugin.

:copyright: (c) 2011 by the Linovia, see AUTHORS for more details.
:copyright: (c) 2014 by tinyclues, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages


tests_require = [
    'pytest',
    'mock',
]

install_requires = [
    'sentry>=6.0.0',
    'requests'
]

setup(
    name='sentry-insights',
    version='0.1.1',
    author='Boris Feld',
    author_email='boris.feld@tinyclues.com',
    url='http://github.com/tinyclues/sentry-insights',
    description='A Sentry extension which integrates with New Relic Insights.',
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
            'sentry_insights = sentry_insights ',
        ],
        'sentry.plugins': [
            'insights = sentry_insights.models:InsightsMessage',
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
