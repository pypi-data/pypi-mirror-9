#!/usr/bin/env python3

# Copyright 2014 Louis Paternault
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

"""Installateur"""

from setuptools import setup, find_packages
import codecs
import os

def readme():
    directory = os.path.dirname(os.path.join(
        os.getcwd(),
        __file__,
        ))
    return codecs.open(os.path.join(directory, "README.rst"), "r", "utf8").read()

setup(
        name='Devoir',
        version="0.1.0",
        packages=find_packages(),
        install_requires=[], # Everything in standard library
        setup_requires=["hgtools"],
        include_package_data=True,
        author='Louis Paternault',
        author_email='spalax@gresille.org',
        description='Quickly set up a working environment to edit a file.',
        url='https://git.framasoft.org/spalax/devoir',
        license="GPLv3 or any later version",
        #test_suite="jouets.test:suite",
        entry_points={
            'console_scripts': ['devoir = devoir.main:main']
            },
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Intended Audience :: End Users/Desktop",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Topic :: Utilities",
        ],
        long_description=readme(),
        zip_safe = True,
)
