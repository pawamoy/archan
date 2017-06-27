#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Setup script.

Uses setuptools.
Long description is a concatenation of README.rst and CHANGELOG.rst.
"""

from __future__ import absolute_import, print_function

import io
import re
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup


def read(*names, **kwargs):
    """Read a file in current directory."""
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()

ARCHAN_EP = [
    'archan.LayeredArchitecture = archan.checkers:LayeredArchitecture',
    'archan.SeparationOfPrivileges = archan.checkers:SeparationOfPrivileges',
    'archan.LeastPrivileges = archan.checkers:LeastPrivileges',
    'archan.EconomyOfMechanism = archan.checkers:EconomyOfMechanism',
    'archan.CodeClean = archan.checkers:CodeClean',
    'archan.OpenDesign = archan.checkers:OpenDesign',
    'archan.LeastCommonMechanism = archan.checkers:LeastCommonMechanism',
    'archan.CompleteMediation = archan.checkers:CompleteMediation',
    'archan.CSVInput = archan.providers:CSVInput'
]


setup(
    name='archan',
    version='2.0.1',
    license='ISC',
    description='Analysis of your architecture strength based on DSM data.',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S)
        .sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author=u'Timothee Mazzucotelli',
    author_email='timothee.mazzucotelli@gmail.com',
    url='https://github.com/Pawamoy/archan',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    keywords=[
        'archan', 'architecture', 'analysis', 'security', 'dsm', 'audit'
    ],
    install_requires=[
        'colorama', 'pyyaml'
    ],
    extras_require={
        # 'with_dependenpy': ['dependenpy'],
    },
    entry_points={
        'console_scripts': ['archan = archan.cli:main'],
        'archan': ARCHAN_EP
    },
)
