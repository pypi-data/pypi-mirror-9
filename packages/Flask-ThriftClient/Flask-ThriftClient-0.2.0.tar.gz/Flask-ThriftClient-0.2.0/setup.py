#!/usr/bin/env python
"""
Flask-ThriftClient
-----------

Adds thrift client support to your Flask application

"""

import os
from setuptools import setup

here = os.path.dirname(__file__)
readme_path = os.path.join(here, 'README.rst')
long_description = ""
with open(readme_path) as fd:
	long_description = fd.read()


setup(
	name='Flask-ThriftClient',
	version='0.2.0',
	url='https://bitbucket.org/chub/flask-thriftclient',
	license='BSD',
	author='Pierre Lamot',
	author_email='pierre.lamot@yahoo.fr',
	description='Adds thrift client support to your Flask application',
	long_description=long_description,
	packages=[
		'flask_thriftclient',
	],
	zip_safe=False,
	platforms='any',
	install_requires=[
		'Flask>=0.7',
		'thrift>=0.8'
	],
	test_suite='tests.thriftclient',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'Framework :: Flask',
		'License :: OSI Approved :: BSD License',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2 :: Only',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Software Development :: Libraries :: Python Modules'
	]
)
