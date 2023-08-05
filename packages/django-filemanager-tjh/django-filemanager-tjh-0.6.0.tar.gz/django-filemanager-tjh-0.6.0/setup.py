#!/usr/bin/env python
"""
Install django-filemanager using setuptools
"""

from setuptools import setup, find_packages
from filemanager import __version__

with open('README.rst') as f:
    readme = f.read()

setup(
    name='django-filemanager-tjh',
    version=__version__,
    description='A django filemanager app',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@timheap.me',
    url='https://bitbucket.org/tim_heap/django-filemanager',

    install_requires=['Django>=1.7'],
    zip_safe=False,

    packages=find_packages(),

    include_package_data=True,
    package_data={},

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
)
