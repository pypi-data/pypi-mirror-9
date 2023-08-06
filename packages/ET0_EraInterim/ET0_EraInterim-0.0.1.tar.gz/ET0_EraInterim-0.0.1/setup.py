#!/usr/bin/env python

# eraInterim Util
#
#
# Author: yoann Moreau
# Contributer: benjamin tadry
#
# License: CC0 1.0 Universal
import sys
import subprocess

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    with open("README.md") as f:
        return f.read()

setup(name="ET0_EraInterim",
      version='0.0.1',
      description="A utility to produce ET0 based on ERA INTERIM data ",
      long_description=readme(),
      author="Yoann M",
      author_email="yoann.moreau@gmail.com",
      scripts=["python/utils.py","python/calculateETfromERAI.py"],
      url="https://github.com/yoannMoreau/ET0_EraInterim",
      packages=["python"],
      include_package_data=True,
      license="CCO",
      platforms="Posix; ",
      install_requires=[
          "GDAL",
          "OGR", 
          "ecmwfapi"
      ],
      classifiers = ["Development Status :: 3 - Alpha"]
      )
