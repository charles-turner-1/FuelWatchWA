#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
with open("README.md","r") as fh:
  long_description = fh.read()

setup(
  url = "https://github.com/charles-turner-1/Fuelwatch",
  author="Charles Turner",
  author_email='charlesturner0987@gmail.com',
  classifiers=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],
  install_requires=["requests","feedparser", "pandas"
                   ,"geocoder"],
  extras_require = {"dev": ["pytest>=3.7",],},
  description="Fuelwatch Stuff",
  py_modules=["Fuelwatch"],
  package_dir={'': 'src'},
  license="MIT license",
  include_package_data=True,
  name='Fuelwatch',
  version='0.0.1',
  zip_safe=False,
  long_description=long_description,
  long_description_content_type="text/markdown",
)
