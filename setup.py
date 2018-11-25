#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='DEMONSTRATOR_PROGRAM_API',
      version='0.0.1',
      description='FAPS Demonstrator program api',
      license='MIT',
      author='FAU - FAPS',
      author_email='jupiter.bakakeu@faps.fau.de',
      url='https://faps.de/',
      # packages=find_packages(exclude = ['ppo']),
      install_requires=required,
      long_description='FAPS Demonstrator API. This api enable the control of the demonstrator from the cloud.')
