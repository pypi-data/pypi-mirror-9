#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import codecs
import re
import sys

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read("README.rst") + "\n\n" + read("HISTORY.rst")

requirements = []
test_requirements = []

if sys.version_info[:2] < (2, 7):
    test_requirements.append("unittest2")

setup(
    name="csv_object_reader",
    version=find_version("csv_object_reader", "__init__.py"),
    description="CSV file reader which returns objects",
    long_description=long_description,
    author="fireyone29",
    author_email="fireyone29@gmail.com",
    url="https://github.com/fireyone29/csv_object_reader",
    packages=["csv_object_reader"],
    package_dir={"csv_object_reader": "csv_object_reader"},
    include_package_data=True,
    install_requires=requirements,
    test_suite="tests",
    tests_require=test_requirements,
    license="MIT",
    zip_safe=False,
    keywords="csv_object_reader, csv",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ]
)
