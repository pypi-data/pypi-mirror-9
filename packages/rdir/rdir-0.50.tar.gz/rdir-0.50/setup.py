#!/usr/bin/python
# coding: utf-8
__author__ = 'lhfcws'

from setuptools import setup, find_packages

setup(
      name="rdir",
      version="0.50",
      description="More powerful recursive dir. Support HTML pretty view in tree structure.",
      author="Lhfcws Wu",
      author_email="lhfcws@gmail.com",
      url="http://www.github.com/Lhfcws/rdir",
      license="MIT",
      packages=find_packages(),
      install_requires=['colorama', 'pyquery'],
      keywords=["dir", "doc", "pydoc", "html"],
)
