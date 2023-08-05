#!/usr/bin/python

import sys
import os
from distutils.core import setup
from distutils.errors import *

if sys.version_info < (2, 4) or sys.version_info[0] == 3:
    raise DistutilsError("This package requires Python 2.4 or higher versions 2.x not Python3")

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),r"src/UcsSdk"))
from Version import __version__

name='UcsSdk'

def is_package(path):
	return (
			os.path.isdir(path) and
			os.path.isfile(os.path.join(path, '__init__.py'))
			)

def find_packages(path, base="" ):
	packages = {}
	for item in os.listdir(path):
		dir = os.path.join(path, item)
		if is_package( dir ):
			if base:
				module_name = "%(base)s.%(item)s" % vars()
			else:
				module_name = item
			packages[module_name] = dir
			packages.update(find_packages(dir, module_name))
	return packages

setup(
	name=name,
	version=__version__,
	description='Python SDK for Cisco UCS Manager',
	author='Cisco Systems',
	author_email='',
	long_description='Install Instructions: sudo python setup.py install',
        url='https://github.com/CiscoUcs/UcsPythonSDK',
        download_url='https://github.com/CiscoUcs/UcsPythonSDK/tarball/0.8.1.5',
	license='LICENSE.txt',
	packages=find_packages('src'),
	package_dir = {'': 'src'},
	namespace_packages=['UcsSdk'],
	package_data={'': ['resources/*.xml']},
        include_package_data = True,
        zip_safe = False,
	)
