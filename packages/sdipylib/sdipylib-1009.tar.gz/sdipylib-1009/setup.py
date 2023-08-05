#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sdipylib


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

packages = [
    'sdipylib'
]

scripts=[

]

package_data = {"": []}

requires = ['boto']

classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name='sdipylib',
    version=sdipylib.__version__,
    description='San Diego Regional Data LIbrary library for IPython data analysis',
    long_description=readme,
    packages=packages,
    package_data=package_data,
    scripts=scripts,
    install_requires=requires,
    author=sdipylib.__author__,
    author_email='eric@sandiegodata.org',
    url='https://github.com/sdrdl/sdipylib',
    license='BSD',
    classifiers=classifiers,
)
