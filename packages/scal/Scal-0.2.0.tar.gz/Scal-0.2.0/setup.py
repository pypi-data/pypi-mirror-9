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

"""Installer"""

from setuptools import setup, find_packages
import os

def readme():
    directory = os.path.dirname(os.path.join(
        os.getcwd(),
        __file__,
        ))
    return open(os.path.join(directory, "README.rst"), "r").read()

setup(
        name='Scal',
        version="0.2.0",
        packages=find_packages(),
        setup_requires=["hgtools"],
        install_requires=[
            "jinja2",
            ],
        include_package_data=True,
        author='Louis Paternault',
        author_email='spalax@gresille.org',
        description='LaTeX generation of school year calendars',
        url='http://git.framasoft.org/spalax/scal',
        license="GPLv3 or any later version",
        test_suite="scal.test.suite",
        entry_points={
            'console_scripts': ['scal = scal.main:main']
            },
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Education",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Topic :: Software Development :: Code Generators",
            "Topic :: Text Processing :: Markup :: LaTeX",
        ],
        long_description=readme(),
        zip_safe = True,
)
