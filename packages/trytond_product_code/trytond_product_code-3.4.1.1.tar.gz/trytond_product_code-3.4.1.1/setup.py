#!/usr/bin/env python
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from setuptools import setup, Command
import re
import os
import ConfigParser
import unittest
import sys


class SQLiteTest(Command):
    """
    Run the tests on SQLite
    """
    description = "Run tests on SQLite"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.environ['TRYTOND_DATABASE_URI'] = 'sqlite://'
        os.environ['DB_NAME'] = ':memory:'

        from tests import suite
        test_result = unittest.TextTestRunner(verbosity=3).run(suite())

        if test_result.wasSuccessful():
            sys.exit(0)
        sys.exit(-1)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

MODULE2PREFIX = {
    'product_notebook': 'openlabs',
}

requires = []
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append('%s_%s >= %s.%s, < %s.%s' % (
            MODULE2PREFIX.get(dep, 'trytond'), dep, major_version,
            minor_version, major_version, minor_version + 1)
        )
requires.append('trytond >= %s.%s, < %s.%s' %
        (major_version, minor_version, major_version, minor_version + 1))

setup(
    name='trytond_product_code',
    version=info.get('version', '0.0.1'),
    description='Tryton module for adding multiple product codes',
    long_description=read('README.rst'),
    author='Openlabs Technologies & Consulting (P) Limited',
    url='https://github.com/openlabs/trytond-product-code',
    package_dir={'trytond.modules.product_code': '.'},
    packages=[
        'trytond.modules.product_code',
        'trytond.modules.product_code.tests',
    ],
    package_data={
        'trytond.modules.product_code': info.get(
            'xml', []) + ['tryton.cfg', 'locale/*.po', 'icons/*.svg'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Legal Industry',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
    ],
    license='GPL-3',
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    product_code = trytond.modules.product_code
    """,
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
    cmdclass={
        'test': SQLiteTest,
    },
)
