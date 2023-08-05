#!/usr/bin/python
# coding: utf-8
__author__ = 'lhfcws'

from setuptools import setup, find_packages

setup(
      name="rdir",
      version="0.51",
      description="More powerful recursive dir. Support HTML pretty view in tree structure.",
      author="Lhfcws Wu",
      author_email="lhfcws@gmail.com",
      url="http://www.github.com/Lhfcws/rdir",
      license="MIT",
      packages=find_packages(),
      include_package_data=True,
      package_data={"rdir": ["rdir/generateHTML/template/*.html", "rdir/generateHTML/bin/js/*.js"]},
      install_requires=['colorama', 'pyquery'],
      keywords=["dir", "doc", "pydoc", "html"],
)
