# -*- coding: utf-8 -*-
#
# dev-init - automated development environment initialization
# https://github.com/rmed/dev-init
#
# Copyright (C) 2014  Rafael Medina García <rafamedgar@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "DESCRIPTION.rst")) as f:
    long_description = f.read()

setup(
    name='dev-init',
    version='0.3.0',

    description='Automated development environment initialization',
    long_description=long_description,

    url='https://github.com/rmed/dev-init',

    author='Rafael Medina García',
    author_email='rafamedgar@gmail.com',

    license='GPLv3',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='development environment automated initialization dev init',

    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'dev-init = dev_init.dev_init:main'
        ]
    }
)
