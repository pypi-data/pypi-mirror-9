#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
		name = 'projectlib',
		version = '0.0.1',
		keywords = ('libproject', 'project'),
		description = 'zhaowenlei upload projectlib',
		license = 'MIT License',

		url = 'http://liluo.org',
		author = 'liluo',
		author_email = 'zhaowenlei789@sina.com',

		packages = find_packages(),
		include_package_data = True,
		platforms = 'any',
		install_requires = [],
)

