#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pedro Tome <pedro.tome@idiap.ch>
# @date: Tue 25 Jun 18:18:08 2014 CEST
#
# Copyright (C) 2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# This file contains the python (distutils/setuptools) instructions so your
# package can be installed on **any** host system. It defines some basic
# information like the package name for instance, or its homepage.
#
# It also defines which other packages this python package depends on and that
# are required for this package's operation. The python subsystem will make
# sure all dependent packages are installed or will install them for you upon
# the installation of this package.
#
# The 'buildout' system we use here will go further and wrap this package in
# such a way to create an isolated python working environment. Buildout will
# make sure that dependencies which are not yet installed do get installed, but
# **without** requiring adminstrative privileges on the host system. This
# allows you to test your package with new python dependencies w/o requiring
# administrative interventions.

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all parameters that define our package.
setup(

    # Basic information about the project
    name='antispoofing.fvcompetition_icb2015',
    version='2.0.0',
    description='Running the competition results: "The 1st Competition on Counter Measures to Finger Vein Spoofing Attacks".',

    # Additional information of the package
    url='https://github.com/bioidiap/antispoofing.fvcompetition_icb2015.git',
    license='LICENSE.txt',
    author='Pedro Tome',
    author_email='pedro.tome@idiap.ch',

    # The description that is shown on the PyPI page
    long_description=open('README.rst').read(),

    # The definition of what is provided by this package
    packages=find_packages(),
    include_package_data=True,

    # This line defines which packages should be installed when you "install" this package.
    # All packages that are mentioned here, but are not installed on the current system will be installed locally and only visible to the scripts of this package.
    # Don't worry - You won't need adminstrative privileges when using buildout.
    install_requires=[
      'setuptools',
      'bob.io.base',
      'bob.core',
      'bob.ip.base',
      'bob.sp',
      'bob.measure',
      'bob.io.image',
    
    ],

    # This defines a namespace package so that other projects can share this namespace.
    namespace_packages = [
      'antispoofing',   
      'antispoofing.fvcompetition_icb2015',
    ],

    # Here, the entry points (resources) are registered.
    entry_points = {
      # Register four console scripts, one for executing the experiments, one for evaluating the results, one for categorical calibration and one for generating the plots
      'console_scripts': [
        'icb2015_baseline_countermeasure.py = antispoofing.fvcompetition_icb2015.baseline_countermeasure:main',
        'icb2015_evaluation_results.py = antispoofing.fvcompetition_icb2015.evaluation_results:main',

      ],

            
    },

    # Classifiers for PyPI
    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python :: 2.7',
      'Environment :: Console',
      'Framework :: Buildout',
      'Topic :: Scientific/Engineering',
    ],
)
