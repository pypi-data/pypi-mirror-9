#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from pytest_pipeline import __author__, __contact__, \
        __homepage__, __version__


with open("README.rst") as src:
    readme = src.read()
with open("HISTORY.rst") as src:
    history = src.read().replace(".. :changelog:", "")

with open("requirements.txt") as src:
    requirements = [line.strip() for line in src]
with open("requirements-dev.txt") as src:
    test_requirements = [line.strip() for line in src]


setup(
    name="pytest-pipeline",
    version=__version__,
    description="Pytest plugin for functional testing of data analysis pipelines",
    long_description=readme + "\n\n" + history,
    author=__author__,
    author_email=__contact__,
    url=__homepage__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords="pytest pipeline plugin testing",
    tests_require=test_requirements,
    entry_points={
        "pytest11": [
            "pytest-pipeline = pytest_pipeline.plugin",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Utilities",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries",
    ],
)
