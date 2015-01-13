#!/usr/bin/env python

'''
setup.py - Python distutils setup file for RoverPylot package.

Copyright (C) 2014 Simon D. Levy

This code is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This code is distributed in the hope that it will be useful,     
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License 
along with this code.  If not, see <http://www.gnu.org/licenses/>.
'''

#from distutils.core import setup
from setuptools import setup

setup (name = 'RoverPylot',
    version = '0.1',
    install_requires = ['pygame'],
    description = 'Python API for the Brookstone Rover 2.0 and Rover Revolution',
    packages = ['rover'],
    author='Simon D. Levy',
    author_email='simon.d.levy@gmail.com',
    url='http://home.wlu.edu/~levys/software/roverpylot',
    license='LGPL',
    platforms='Linux; Windows'
    )
    
