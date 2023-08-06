#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name = 'WarpedLMM',
      version='0.21',
      author='Nicolo Fusi',
      author_email="fusi@microsoft.com",
      description=("Warped linear mixed model"),
      license="Apache 2.0",
      keywords="genetics GWAS",
      packages = ["warpedlmm", 'warpedlmm.testing', 'warpedlmm.util'],
      install_requires=['scipy>=0.13', 'numpy>=1.6', 'matplotlib>=1.2', 'nose', 'fastlmm>=0.2.1', 'pandas', 'pysnptools'],
      classifiers=[
      "License :: OSI Approved :: Apache Software License"],
      )
