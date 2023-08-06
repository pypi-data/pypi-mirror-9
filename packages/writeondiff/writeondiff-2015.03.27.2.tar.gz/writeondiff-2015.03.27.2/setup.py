#!/usr/bin/python

from setuptools import setup
from version import VERSION

if __name__ == '__main__':
	setup(
		name="writeondiff",
		version=VERSION,
		install_requires=[
			'argparse',
		],
		packages = ['_writeondiff'],
		package_dir = {'_writeondiff': ''},
		entry_points = {'console_scripts': ['writeondiff = _writeondiff.writeondiff:main',]},
		zip_safe=False,
	)
