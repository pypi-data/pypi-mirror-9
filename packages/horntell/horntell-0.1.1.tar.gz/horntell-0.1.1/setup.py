import os
import sys
import warnings

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

try:
	from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
	from distutils.command.build_py import build_py

install_requires = []

if sys.version_info < (2, 6):
	warnings.warn(
		'Python 2.5 is not supported by Horntell. '
		'If you have any questions, please file an issue on Github or '
		'contact us at friends@horntell.com.',
		DeprecationWarning)
	install_requires.append('requests >= 0.8.8, < 0.10.1')
else:
	install_requires.append('requests >= 0.8.8')


# Get simplejson if we don't already have json
if sys.version_info < (3, 0):
	try:
		from util import json
	except ImportError:
		install_requires.append('simplejson')

setup(
	name='horntell',
	version='0.1.1',
	description='Horntell SDK for Python',
	cmdclass={'build_py': build_py},
	author='Mohit Mamoria',
	author_email='mohit@horntell.com',
	packages=['horntell', 'horntell.http'],
	url='https://github.com/horntell/python-sdk',
	install_requires=install_requires,
	use_2to3=True
)