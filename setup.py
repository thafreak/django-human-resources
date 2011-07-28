#!/usr/bin/env python


import setuptools
from distutils.core import setup
import os, sys

version = __import__('hr').VERSION


setup(
    name = 'django-hr',
    #version = version,
    description = "A simple django admin-powered application that allows businesses to manage their human resources workflows.",
    author = 'Ryan Archdeacon',
    author_email = 'ryan@theprojecta.com',
    url = 'https://github.com/archie86/django-hr',
    packages = ['legal'],
    include_package_data=True,
	install_requires=[
		'Django>=1.2',
    ],
)
