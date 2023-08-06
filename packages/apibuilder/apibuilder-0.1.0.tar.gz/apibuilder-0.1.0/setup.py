#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
        name = "apibuilder",
        version = "0.1.0",
        packages = find_packages(),

        # Dependencies
        install_requires = [
            "flask >= 0.10.0",
            "flask-basicauth >= 0.2.0",
            "flask-mongoengine >= 0.7.0",
            "requests >= 2.5.0"
        ],

        # Testing
        tests_require = [
            "nose >= 1.3",
            "responses >= 0.3"
        ],

        # Metadata
        author = "Douglas Chambers",
        author_email = "leonchambers@mit.edu",
        description = "Library for building simple REST APIs and clients",
        url = "http://github.com/MIT-CityFARM/apibuilder"
)
