#!/usr/bin/env python
from setuptools import setup

setup(name='robotframework-radius',
      version='0.1.1',
      description='Robotframework RADIUS library',
      author='Michael van Slingerland',
      author_email='michael@deviousops.nl',
      url='https://github.com/deviousops/robotframework-radius',
      packages     = ['RadiusLibrary'],
      install_requires=[
        "robotframework",
        "pyrad"
      ],
      classifiers = [
        "License :: OSI Approved :: Apache Software License"
      ]
 )
