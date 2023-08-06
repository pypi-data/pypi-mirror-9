#!/usr/bin/env python

"""
Bugsnag
=======

The official Python notifier for `Bugsnag <https://bugsnag.com/>`_.
Provides support for automatically capturing and sending exceptions
in your Django and other Python apps to Bugsnag, to help you find
and solve your bugs as fast as possible.
"""

from setuptools import setup, find_packages

tests_require = [
  'tornado',
  'flask',
  'webob',
  'blinker',
  'django',
  'celery',
  'webtest',
  'mock',
  'nose',
]

setup(
    name='bugsnag',
    version='2.3.1',
    description='Automatic error monitoring for django, flask, etc. (https://bugsnag.com).',
    long_description=__doc__,
    author='Simon Maynard',
    author_email='simon@bugsnag.com',
    url='https://bugsnag.com/',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development'
    ],
    test_suite='nose.collector',
    install_requires=['webob'],
    tests_require=tests_require,
    extras_require={
        'flask': ['flask', 'blinker'],
        'tests': tests_require,
    },
)
