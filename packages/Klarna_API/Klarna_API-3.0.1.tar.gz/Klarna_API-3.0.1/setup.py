#!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
	name="Klarna_API",
	version="3.0.1",
	author='Merchant Integration',
	author_email='support@klarna.com',
	description=("The Klarna API used to communicate with Klarna Online"),
	license="BSD",
	keywords="klarna xmlrpc payment",
	url="https://developers.klarna.com",
	packages=['klarna', 'klarna.checkout', 'klarna.pclasses', 'klarna.kex'],
	long_description=read('README'),
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: BSD License",
		"Natural Language :: English",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 3",
		"Topic :: Software Development :: Libraries :: Python Modules"
	],
)
