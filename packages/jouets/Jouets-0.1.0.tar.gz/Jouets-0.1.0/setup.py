#!/usr/bin/env python3

# Copyright 2014 Louis Paternault
#
# This file is part of Jouets.
#
# Jouets is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jouets is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jouets.  If not, see <http://www.gnu.org/licenses/>.

"""Installer"""

from setuptools import setup, find_packages
import codecs
import glob
import os
import sys

def readme():
    directory = os.path.dirname(os.path.join(
        os.getcwd(),
        __file__,
        ))
    with codecs.open(os.path.join(directory, "README.rst"), mode="r") as file:
        return file.read()

def get_binary_names():
    return [os.path.basename(binary) for binary in glob.glob(os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'bin', '*'))]

setup(
        name='Jouets',
        version="0.1.0",
        packages=find_packages(),
        setup_requires=["hgtools"],
        install_requires=[
            "jinja2",
            "pluginbase",
            ],
        include_package_data=True,
        author='Louis Paternault',
        author_email='spalax@gresille.org',
        description='Bric-à-brac de programmes mathématiques « amusants »',
        url='https://git.framasoft.org/spalax/jouets',
        license="GPLv3 or any later version",
        test_suite="jouets.test.suite",
        entry_points={
            'console_scripts': [
                "{name} = jouets.{binary}:main".format(
                    name=binary.split('.')[-1],
                    binary=binary,
                    ) for binary in get_binary_names()
                ],
            },
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.4",
            "Topic :: Games/Entertainment",
            "Intended Audience :: Education",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Topic :: Education",
            "Topic :: Scientific/Engineering :: Mathematics",
            ],
        long_description=readme(),
        zip_safe=False,
)
