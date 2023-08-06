#!/usr/bin/python

from setuptools import setup
from version import VERSION

if __name__ == '__main__':
	setup(
		name="pmcc",
		version=VERSION,
		packages = ['_pmcc'],
		package_dir = {'_pmcc': ''},
		entry_points = {'console_scripts': ['pmcc = _pmcc.pmcc:main']},
		zip_safe=False,
	)
