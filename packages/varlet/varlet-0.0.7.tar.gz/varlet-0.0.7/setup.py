#!/usr/bin/env python
from setuptools import setup
import sys

if sys.version_info < (3,):
    install_requires = ['importlib']
    extras_require = {
        'test': ['mock']
    }
else:
    install_requires = []
    extras_require = {}

setup(
    name="varlet",
    version='0.0.7',
    author='Matt Johnson',
    author_email='mdj2@pdx.edu',
    description="Interactive prompt for variables that should be set at runtime",
    packages=['varlet'],
    zip_safe=False,
    classifiers=[
        'Framework :: Django',
    ],
    install_requires=install_requires,
    extras_require=extras_require
)
