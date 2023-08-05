#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
Flask-BigTempo
--------------

Flask extension created to enable a flask server to provide bigtempo functions.
'''


import os
import sys


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


import re
import pkgutil

import flask_bigtempo


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


def filter_comments(contents):
    filter_pattern = re.compile(r'[\s]*#.*')
    return filter(lambda x: not filter_pattern.match(x), contents)


def packages(path=None, prefix="", exclude=None):
    try:
        return find_packages(exclude=exclude)
    except:
        return [name for _, name, ispkg in pkgutil.walk_packages(path, prefix) if ispkg]


setup(
    name='flask-bigtempo',
    version=flask_bigtempo.__version__,
    description="Flask extension for bigtempo features",
    long_description=read('README.md'),
    license=read('LICENSE'),

    author="Roberto Haddock Lobo",
    author_email="rhlobo+bigtempo@gmail.com",
    url='https://github.com/rhlobo/flask-bigtempo',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    platforms='any',

    install_requires=filter_comments(read('requirements.txt').split('\n')),
    packages=packages(flask_bigtempo.__path__,
                      flask_bigtempo.__name__,
                      exclude=["*.tests",
                               "*.tests.*",
                               "tests.*",
                               "tests"]),
    package_data={'': ['README.md',
                       'LICENSE',
                       'requirements.txt',
                       'scripts/store_api']},
    scripts=['scripts/store_api'],

    include_package_data=True,
    zip_safe=False
)
