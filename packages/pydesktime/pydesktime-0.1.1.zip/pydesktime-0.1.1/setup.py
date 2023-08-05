#!/usr/bin/env python
# coding=utf-8
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

LICENSE = open(
    os.path.join(os.path.dirname(__file__), 'LICENSE')).read().strip()
DESCRIPTION = open(
    os.path.join(os.path.dirname(__file__), 'README.rst')).read().strip()

requires = [
    'requests'
]

setup(name='pydesktime',
      version='0.1.1',
      description='Module to communicate with Desktime API',
      long_description=DESCRIPTION,
      classifiers=[
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet :: WWW/HTTP",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      author='Łukasz Bołdys',
      author_email='mail@utek.pl',
      url='http://github.com/utek/pydesktime',
      keywords='api',
      license=LICENSE,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pydesktime',
      install_requires=requires,
      entry_points="""\
      """,
      )
