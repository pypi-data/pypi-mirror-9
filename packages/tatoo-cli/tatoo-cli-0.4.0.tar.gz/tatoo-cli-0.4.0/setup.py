#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=all
import os
import sys
import codecs
from setuptools import setup, find_packages

PY3 = sys.version_info[0] == 3

NAME = 'tatoo-cli'

if sys.version_info < (2, 6):
    raise Exception('tatoo-cli requires python 2.6 or higher.')

here = os.path.abspath(os.path.dirname(__file__))

# -*- Classifiers -*-
classifiers = """
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    Natural Language :: English
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.6
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
"""
classifiers = [s.strip() for s in classifiers.split('\n') if s]

# -*- Distribution meta -*-
meta = {}
with open(os.path.join(here, 'src', NAME.replace('-', '_'), '_version.py')) as f:
    for line in f:
        key, value = line.split('=')
        meta[key.strip()] = value.strip("' \n")


# -*- Requirements -*-
def strip_comments(l):
    return l.lstrip('#').strip()


def reqs(*f):
    requirements = []
    with open(os.path.join(os.getcwd(), 'requirements', *f)) as file_:
        for line in file_:
            requirements.append(strip_comments(line))
    return requirements

default_reqs = reqs('default.txt')

# -*- Test requirements -*-
test_reqs = reqs('test.txt')

# -*- Long description -*-
long_description = codecs.open('README.rst', 'r', 'utf-8').read()

# -*- Entry points -*-
entry_points = """
    [console_scripts]
    tatoo = tatoo_cli.commands:umbrella
    [tatoo.extensions]
    cli = tatoo_cli.extension:ext
"""
# -*- Extra requirements -*-
extras_require = {
    ":python_version=='2.6' or python_version=='2.7'": reqs('py2.txt'),
}
extra = {'extras_require': extras_require}

# -*- Setup -*-
setup(
    name=NAME,
    version=meta['VERSION']+meta['SERIES'],
    description='Command-line interface for tatoo library',
    author=meta['__author__'],
    author_email=meta['__contact__'],
    url=meta['__homepage__'],
    platforms=['linux', 'osx', 'windows'],
    license='BSD-3',
    keywords='tatoo cli command line interface',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=False,
    zip_safe=True,
    install_requires=default_reqs,
    tests_require=test_reqs,
    test_suite='nose.collector',
    classifiers=classifiers,
    entry_points=entry_points,
    long_description=long_description,
    **extra
)
