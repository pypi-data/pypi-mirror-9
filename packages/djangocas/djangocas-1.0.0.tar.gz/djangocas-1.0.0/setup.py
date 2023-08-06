#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    author='mdj2',
    author_email='mdj2@pdx.edu',
    description='CAS 1.0/2.0 authentication backend for Django',
    license='MIT',
    long_description="""
``djangocas`` is a `CAS`_ 1.0 and CAS 2.0 authentication backend for
`Django`_. It allows you to use Django's built-in authentication mechanisms
and ``User`` model while adding support for CAS.

It also includes a middleware that intercepts calls to the original login and
logout pages and forwards them to the CASified versions, and adds CAS support
to the admin interface.

.. _Django: http://www.djangoproject.com/
""",
    name='djangocas',
    packages=['djangocas'],
    url='https://github.com/mdj2/djangocas',
    version='1.0.0',
    install_requires=[
        'six',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
