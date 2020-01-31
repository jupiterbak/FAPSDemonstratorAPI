#!/usr/bin/env python

import setuptools

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
      name='FAPSDemonstratorAPI',
      version='0.0.5',
      description='FAPS Demonstrator FAPSDemonstratorAPI api',
      license='MIT',
      author='FAU - FAPS',
      author_email='jupiter.bakakeu@faps.fau.de',
      url='https://faps.de/',
      packages=setuptools.find_packages(),
      install_requires=required,
      classifiers=[
              "Programming Language :: Python :: 3",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent",
          ],
      long_description='FAPS Demonstrator API. This api enable the control of the demonstrator from the cloud.'
)
