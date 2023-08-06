# -*- coding: utf-8 -*-
# Copyright 2013 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
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

from __future__ import absolute_import, print_function

import os
import sys
from setuptools import setup, find_packages
requirements = ["cobra>=3.2"]

setup(
    name='driven',
    version="0.0.0",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    author='Joao Cardoso',
    author_email='jooaaoo@gmail.com',
    description='driven - data-driven constraint-based analysis',
    license='Apache License Version 2.0',
    keywords='biology metabolism bioinformatics high-throughput',
    url='TBD',
    long_description="A package for data driven modeling and analysis.",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: Apache Software License'
    ],
)
