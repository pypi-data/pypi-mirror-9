#!/usr/bin/env python
from setuptools import setup


setup(name="log2c",
      version="0.0.2",
      description="Crawling 2-channel threads in log",
      author="castaneai",
      author_email="castaneai@castaneai.net",
      url="",
      py_modules=['log2c'],
      install_requires=open("requirements.txt").read().splitlines())
