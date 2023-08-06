#!/usr/bin/env python

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
import codecs
import os

def readme():
    directory = os.path.dirname(os.path.join(
        os.getcwd(),
        __file__,
        ))
    return codecs.open(os.path.join(directory, "README.rst"), "r", "utf8").read()

setup(
        name='sphinxcontrib-packages',
        version="0.1.0",
        packages=find_packages(),
        setup_requires=["hgtools"],
        install_requires=[
            "sphinx",
            ],
        include_package_data=True,
        author='Louis Paternault',
        author_email='spalax@gresille.org',
        description='This packages contains the Packages sphinx extension, which provides directives to display packages installed on the host machine',
        url='http://git.framasoft.org/spalax/packages',
        license="GPLv3 or any later version",
        test_suite="sphinxcontrib.packages.test.suite",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Framework :: Sphinx :: Extension",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
            "Operating System :: Unix",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.4",
            "Topic :: Documentation :: Sphinx",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        long_description=readme(),
        zip_safe = False,
)
