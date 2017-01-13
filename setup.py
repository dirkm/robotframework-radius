#!/usr/bin/env python
from setuptools import setup

VERSION = '0.3.1'
setup(name='robotframework-radius',
      version=VERSION,
      description='Robotframework RADIUS library',
      author='Michael van Slingerland',
      author_email='michael@deviousops.nl',
      url='https://github.com/deviousops/robotframework-radius',
      download_url='https://github.com/deviousops/robotframework-radius/archive/{}.tar.gz'.format(VERSION),
      packages     = ['RadiusLibrary'],
      install_requires=[
        "robotframework",
        "pyrad"
      ],
      classifiers = [
        "License :: OSI Approved :: Apache Software License"
      ],
      long_description=open('README.rst').read(),
 )
