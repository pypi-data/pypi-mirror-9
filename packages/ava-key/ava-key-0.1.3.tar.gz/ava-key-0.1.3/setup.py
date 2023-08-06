# -*- coding: utf-8 -*-

"""
This is a setup.py script for packaging Windows executable.

Usage:
    python setup.py build
"""

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="ava-key",
    version="0.1.3",
    description="Key generator and validator.",
    zip_safe=True,
    author='Sam Kuo',
    author_email='sam@eavatar.com',
    license='BSD',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    long_description=read('README.rst'),
    install_requires=[
        "base58>=0.2.1",
        "click>=3.3",
        "libnacl>=1.4.1",
        "pyscrypt>=1.6.2",
    ],
    entry_points={
        'console_scripts': [
            'ava-key = ava.key:cli',
        ]
    }
)