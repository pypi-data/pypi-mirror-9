from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'Tim Martin'
__pkg_name__ = 'ripozo'

from setuptools import setup, find_packages

import os

version = '0.1.20'

base_dir = os.path.dirname(__file__)

# with open(os.path.join(base_dir, 'README.rst'), 'r+b') as readme:
#     long_description = readme.read()

setup(
    author=__author__,
    author_email='tim.martin@vertical-knowledge.com',
    name='ripozo',
    version=version,
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    description='An tool for easily making RESTful interfaces',
    # long_description=long_description,
    install_requires=[
        'six>=1.4.1,!=1.7.1',
        'jinja2'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    tests_require=[
        'tox',
        'mock',
        'ripozo-tests'
    ],
    test_suite="tests"
)
