#!/usr/bin/python

from setuptools import setup
from version import VERSION

if __name__ == '__main__':
	setup(
		name="desmime",
		version=VERSION,
		packages = ['_desmime'],
		package_dir = {'_desmime': ''},
		entry_points = {'console_scripts': ['desmime = _desmime.desmime:main']},
		zip_safe=False,
	)
