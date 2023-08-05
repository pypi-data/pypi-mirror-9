#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="c2c.cssmin",
    version="0.7",
    license="MIT License",

    author="Camptocamp",
    author_email="info@camptocamp.com",
    url="https://github.com/camptocamp/c2c.cssmin",

    description="A command to merge and compress css files",
    long_description=open("README.rst").read(),

    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License"
    ],

    keywords=["css", "cssmin"],
    install_requires=["cssmin"],
    packages=find_packages(),
    test_suite="c2c.cssmin",
    entry_points={
        "console_scripts": [
            "c2c-cssmin=c2c.cssmin:main",
        ]
    }
)
