#!/usr/bin/env python

import os.path
import sys

from setuptools import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

setup(
    version='0.1.3',
    url='https://github.com/nathforge/pydentifier',
    name='pydentifier',
    description='Generate Python identifiers from English text',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author='Nathan Reynolds',
    author_email='email@nreynolds.co.uk',
    packages=[
        'pydentifier',
        'pydentifier.en'
    ],
    package_dir={'': 'src'},
    test_suite='tests',
    tests_require=['six'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ]
)
