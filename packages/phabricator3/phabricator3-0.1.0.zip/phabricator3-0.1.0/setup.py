#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='phabricator3',
    version='0.1.0',
    author='Konvexum',
    author_email='info@konvexum.se',
    url='http://github.com/konvexum/python-phabricator',
    description='Phabricator API Bindings',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
		'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
