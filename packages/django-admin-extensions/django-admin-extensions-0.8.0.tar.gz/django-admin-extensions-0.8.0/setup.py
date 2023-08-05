#!/usr/bin/env python
"""
Install django-admin-extensions using setuptools
"""

from adminextensions import __version__

from setuptools import setup, find_packages

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='django-admin-extensions',
    version=__version__,
    description='Simple tools to extend the django admin site',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@timheap.me',
    url='https://bitbucket.org/tim_heap/django-admin-extensions',

    packages=find_packages(),

    package_data={},
    include_package_data=True,

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
