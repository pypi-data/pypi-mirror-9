#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

setup(name="python-kemptech-api",
      version="0.1.2",
      packages=find_packages(),
      author="KEMP Technologies",
      author_email="smcgough@kemptechnologies.com",
      maintainer="Shane McGough",
      maintainer_email="smcgough@kemptechnologies.com",
      description="KEMP Technologies Python API",
      long_description=open('README.rst').read(),
      license="Apache",
      keywords="python api kemptech kemp technologies restfull loadmaster",
      url="http://pypi.python.org/pypi/python-kemptech-api/",
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Topic :: Internet',
      ],
      install_requires=['requests>=2.3.0']
)
