#!/usr/bin/env python
"""
Install django-suggestions using setuptools
"""

from djangosuggestions import __version__

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='django-suggestions',
    version=__version__,
    description='A Django form widget that implements the HTML5 form list element',
    author='Tim Heap',
    author_email='tim@timheap.me',
    url='https://bitbucket.org/tim_heap/django-suggestions',

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
