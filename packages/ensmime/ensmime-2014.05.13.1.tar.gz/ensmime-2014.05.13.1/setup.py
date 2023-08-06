#!/usr/bin/python

from setuptools import setup
from version import VERSION

if __name__ == '__main__':
	setup(
		name="ensmime",
		version=VERSION,
		packages = ['_ensmime'],
		package_dir = {'_ensmime': ''},
		entry_points = {'console_scripts': ['ensmime = _ensmime.ensmime:main']},
		zip_safe=False,
	)
