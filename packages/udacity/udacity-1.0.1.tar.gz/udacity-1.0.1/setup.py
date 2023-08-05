#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'udacity',
    'version': '1.0.1',
    'description': 'Library for interacting with Udacity account data and course progress',
    'long_description': open('README.md').read(),
    'author': 'Ty-Lucas Kelley',
    'author_email': 'tylucaskelley@gmail.com',
    'license': 'MIT',
    'url': 'https://github.com/tylucaskelley/udacity-api-python',
    'download_url': 'https://github.com/tylucaskelley/udacity-api-python/tarball/v1.0.1',
    'install_requires': [
        'bx',
        'nose',
        'requests',
        'python-dateutil'
    ],
    'packages': [
        'udacity'
    ],
    'classifiers': [
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP"
    ],
    'keywords': [
        'education',
        'api',
        'udacity',
        'courses',
        'mooc'
    ],
    'test_suite': 'tests'
}

setup(**config)
