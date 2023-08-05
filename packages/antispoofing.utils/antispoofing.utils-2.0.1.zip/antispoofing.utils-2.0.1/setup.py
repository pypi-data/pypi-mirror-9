#!/usr/bin/env python
#Tiago de Freitas Pereira <tiagofrepereira@gmail.com>
#Sat Jul  9 20:21:55 CEST 2012
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.utils',
    version=version,
    description='Utility package for anti-spoofing countermeasures',
    url='http://pypi.python.org/pypi/antispoofing.utils',
    license='GPLv3',
    author='Tiago de Freitas Pereira, Ivana Chingovska',
    author_email='tiagofrepereira@gmail.com, ivana.chingovska@idiap.ch',
    long_description=open('README.rst').read(),
    keywords='antispoofing utilities, antispoofing databases, bob',

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data = True,
    zip_safe = False,

    install_requires=[
      "setuptools",
      "six",
      "bob.ip.color",
      "bob.ip.draw",
      "bob.learn.linear",
      "bob.measure",
      "bob.learn.libsvm"
    ],

    namespace_packages = [
      'antispoofing',
      ],

    entry_points={
      'console_scripts': [
        'merge_scores.py = antispoofing.utils.script.merge_scores:main',
        'test_db.py = antispoofing.utils.script.test_db:main',
        ],
      },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
	)
