#!/usr/bin/python
# coding: utf-8
__author__ = 'lhfcws'

from setuptools import setup, find_packages

setup(
      name="rdir",
      version="0.52",
      description="More powerful recursive dir. Support HTML pretty view in tree structure.",
      long_description="Documentation and bug repot: http://www.github.com/Lhfcws/rdir\n \
                       Sorry for the deploy bugs in the previous versions\n \
                       If you came across ImportError or NoScriptError, please `rm /usr/local/bin/rdir*`",
      author="Lhfcws Wu",
      author_email="lhfcws@gmail.com",
      url="http://www.github.com/Lhfcws/rdir",
      license="MIT",
      packages=["rdir", "rdir/core", "rdir/generateHTML"],
      include_package_data=True,
      package_data={"rdir": ["rdir/generateHTML/template/*.html", "rdir/generateHTML/bin/*.js"]},
      install_requires=['colorama', 'pyquery'],
      keywords=["dir", "doc", "pydoc", "html"],
)
