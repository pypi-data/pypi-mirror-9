#!/usr/bin/env python
# Copyright (C) 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Build script.
"""

import os.path
import sys

sys.path.insert(0, 'src')

from relent import __version__

# We MUST have setuptools
from setuptools import setup, find_packages


def parse_requirements(path):
    with open(path, 'r') as install_reqs:
        return install_reqs.read().splitlines()

reqs = parse_requirements('requirements.txt')


setup(
    name='relent',
    version=__version__,
    author='See AUTHORS',
    url='https://github.com/RHInception/relent',
    license='AGPLv3',
    zip_safe=False,
    packages=find_packages('src'),
    package_dir={
        'relent': 'src/relent',
    },
    package_data={
        'relent': ['*.json'],
    },
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'relent = relent:main',
        ],
    },
    classifiers=[
        ('License :: OSI Approved :: GNU Affero General Public '
         'License v3 or later (AGPLv3+)'),
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
    ],
)
