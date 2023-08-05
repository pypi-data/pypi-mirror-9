#!/usr/bin/env python
from setuptools import setup, find_packages
from codecs import open
from os import path, listdir

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Get the version from the relevant file
with open(path.join(here, 'version'), encoding='utf-8') as f:
    version = f.read().strip()

setup(
    name='constrainingorder',
    version=version,
    packages=find_packages("src"),
    package_dir={"" : "src"},
    include_package_data=True,
    description='Pure python constraint satisfaction solver',
    long_description=long_description,
    install_requires=['future'],
    author="Johannes Reinhardt",
    author_email="jreinhardt@ist-dein-freund.de",
    license="MIT",
    keywords=["csp","constraint","satisfaction","propagation","sets","intervals"],
    url="https://github.com/jreinhardt/constraining-order",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
    ]
)
