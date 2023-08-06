#!/usr/bin/env python

from setuptools import setup, find_packages

# one line description
description = "tools for Mad & Kea"

version = 0.6

setup(name='toMaKe',
      version=version,
      url="https://github.com/mfiers/toMaKe",
      description=description,
      author='Mark Fiers',
      author_email='mark.fiers.42@gmail.com',
      include_package_data=True,
      packages=find_packages(),
      install_requires=[
          'fantail',
          'humanize',
          'jinja2',
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ]
      )
