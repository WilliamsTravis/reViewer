#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 16:58:59 2020

@author: travis
"""

from setuptools import setup


# This is going to require tiledb, gdal, and a few other things.
def check_deps():
    """Check for dependencies, print out which are missing and suggestions
    on how to deal with other issues."""


setup(
    name="review",
    packages=["review"],
    version="0.0.1",
    author="Travis Williams",
    author_email="Travis.Williams@nrel.gov",
    install_requires=["h5py", "numpy", "pandas"]
)
