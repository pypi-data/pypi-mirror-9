#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Fri Aug 23 12:32:01 CEST 2013
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
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

setup(

    name='bob.db.voxforge',
    version=version,
    description='Speaker verification protocol on a subset of the VoxForge database',
    url='http://pypi.python.org/pypi/bob.db.voxforge',
    license='GPLv3',
    keywords = "Speaker Recognition, Speaker verification, Audio processing, Database, Voxforge",
    author='Elie Khoury',
    author_email='Elie.Khoury@idiap.ch',
    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe = False,

    install_requires=[
      'setuptools',
      'bob.db.verification.filelist',
    ],

    namespace_packages = [
      'bob',
      'bob.db',
    ],

    entry_points = {
      # declare database to bob
      'bob.db': [
        'voxforge = bob.db.voxforge.driver:Interface',
      ],
    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Education',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
    ],
)
