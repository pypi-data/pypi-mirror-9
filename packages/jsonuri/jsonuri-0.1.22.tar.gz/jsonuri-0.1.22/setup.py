#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright 2015, Guilherme Dinis J
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
from setuptools import setup

src_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'src')
sys.path.append(src_path)

from jsonuri import __author__, __email__, __license__, __package__, __version__

CLASSIFIERS = [
    'Programming Language :: Python :: 3.4',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Topic :: Software Development'
]

packages = []
root_dir = os.path.dirname("src")


def readme():
    with open('README.md') as fp:
        return fp.read()


def requirements():
    if os.path.exists('requirements.txt'):
        with open('requirements.txt') as fp:
            return fp.readlines()
    else:
        return list()


if root_dir:
    os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('src/'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.').replace("src.", "")
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)

setup(
    name=__package__,
    description="Package to serialize python dictionaries/JSON into URI GET parameters, and reverse.",
    long_description=readme(),
    version=__version__,
    author=__author__,
    author_email=__email__,
    license=__license__,
    url="https://bitbucket.org/guidj/jsonuri-py",
    download_url="https://bitbucket.org/guidj/jsonuri-py/get/v{0}.tar.gz".format(__version__),
    package_dir={'jsonuri': 'src/jsonuri'},
    packages=packages,
    include_package_data=True,
    install_requires=requirements(),
    classifiers=CLASSIFIERS
)


