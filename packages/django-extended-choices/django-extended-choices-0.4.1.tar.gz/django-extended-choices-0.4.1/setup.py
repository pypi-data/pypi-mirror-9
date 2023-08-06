#!/usr/bin/env python

# from __future__ import unicode_literals

from os.path import abspath, dirname, join
from setuptools import setup, find_packages
import sys

def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()

install_requires = ['future']
if sys.version_info < (2, 7):
    install_requires.append('unittest2')

setup(
    name="django-extended-choices",
    version="0.4.1",
    license="GPL",
    description="Little helper application to improve django choices"
    "(for fields)",
    long_description=read_relative_file('README.rst'),
    url="https://github.com/twidi/django-extended-choices",
    author='Stephane "Twidi" Angel',
    author_email="s.angel@twidi.com",
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ]
)
