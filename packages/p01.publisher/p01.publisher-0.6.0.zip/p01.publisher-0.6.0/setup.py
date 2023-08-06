##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: setup.py 4095 2014-07-14 03:19:12Z roger.ineichen $
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='p01.publisher',
    version='0.6.0',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "NO ZODB publisher components for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope zope3 z3c ZODB",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/p01.publisher',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['p01'],
    extras_require=dict(
        test=[
            'zope.testing',
            'p01.checker',
            'p01.testbrowser',
             ]),
    install_requires = [
        'setuptools',
        'ZConfig',
        'p01.cgi',
        'transaction',
        'z3c.jsonrpc',
        'zope.authentication',
        'zope.browser',
        'zope.component',
        'zope.configuration',
        'zope.error',
        'zope.event',
        'zope.i18n',
        'zope.interface',
        'zope.location',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.site',
        'zope.testing',
        'zope.traversing',
        ],
    zip_safe = False,
    entry_points = """
        [paste.app_factory]
        app = p01.publisher.wsgi:application_factory
        """,
)