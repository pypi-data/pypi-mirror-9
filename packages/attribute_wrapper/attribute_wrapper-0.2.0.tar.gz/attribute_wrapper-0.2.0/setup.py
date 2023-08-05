#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from setuptools import setup, find_packages


# Variables ===================================================================
changelog = open('CHANGES.rst').read()
long_description = "\n\n".join([
    open('README.rst').read(),
    changelog
])


# Functions & classes =========================================================
def allSame(s):
    return not filter(lambda x: x != s[0], s)


def hasDigit(s):
    return any(map(lambda x: x.isdigit(), s))


def getVersion(data):
    data = data.splitlines()
    return filter(
        lambda (x, y):
            len(x) == len(y) and allSame(y) and hasDigit(x) and "." in x,
        zip(data, data[1:])
    )[0][0]


setup(
    name='attribute_wrapper',
    version=getVersion(changelog),
    description="Class wrapper, which maps attribute calls to HTTP API.",
    long_description=long_description,
    url='https://github.com/Bystroushaak/attribute_wrapper',

    author='Bystroushaak',
    author_email='bystrousak@kitakitsune.org',

    classifiers=[
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
    ],
    license='MIT',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "setuptools",
        "requests",
    ],
    extras_require={
        "test": [
            "pytest",
        ]
    },
)
