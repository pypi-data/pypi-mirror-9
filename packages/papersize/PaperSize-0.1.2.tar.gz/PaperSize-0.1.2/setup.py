#!/usr/bin python
# -*- coding: utf8 -*-

# Copyright 2015 Louis Paternault
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

"""Installer"""

from setuptools import setup, find_packages
import os

def readme():
    """Return content of the `README.rst` file."""
    directory = os.path.dirname(os.path.join(
        os.getcwd(),
        __file__,
        ))
    return open(os.path.join(directory, "README.rst"), "r").read()

setup(
    name='PaperSize',
    version="0.1.2",
    packages=find_packages(),
    setup_requires=["hgtools"],
    install_requires=[
        ],
    include_package_data=True,
    author='Louis Paternault',
    author_email='spalax@gresille.org',
    description='Paper size related tools',
    url='http://git.framasoft.org/spalax/papersize',
    license="GPLv3 or any later version",
    test_suite="papersize.test.suite",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.4",
        "Topic :: Printing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=readme(),
    zip_safe = True,
)
