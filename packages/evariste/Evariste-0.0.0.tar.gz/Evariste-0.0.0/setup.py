#!/usr/bin/env python3

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
        name='Evariste',
        version="0.0.0",
        packages=find_packages(),
        setup_requires=["hgtools"],
        install_requires=[
            "jinja2",
            "docutils",
            "pygit2",
            ],
        include_package_data=True,
        author='Louis Paternault',
        author_email='spalax@gresille.org',
        description='TODO',
        url='https://git.framasoft.org/spalax/evariste',
        license="GPLv3 or any later version",
        #test_suite="jouets.test:suite", # TODO
        entry_points={
            'console_scripts': ['evariste = evariste.main:main']
            },
        classifiers=[ # TODO
            "Development Status :: 1 - Planning",
        ],
        long_description=readme(),
        zip_safe = False,
)
