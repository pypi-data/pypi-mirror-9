#!/usr/bin/python

from setuptools import setup
from version import VERSION

if __name__ == '__main__':
	setup(
		name="runpulse",
		version=VERSION,
		packages = ['_runpulse'],
		package_dir = {'_runpulse': ''},
		entry_points = {'console_scripts': ['runpulse = _runpulse.runpulse:main']},
		zip_safe=False,
	)
