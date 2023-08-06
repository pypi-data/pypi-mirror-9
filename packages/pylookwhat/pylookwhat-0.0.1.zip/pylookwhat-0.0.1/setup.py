#!/usr/bin/env python

from setuptools import setup
import pylookwhat

setup(
      name="pylookwhat",
      version= pylookwhat.__version__,
      description="look up variables in another python file",
      long_description=open("README.md").read(),
      author="MaxiL",
      author_email="maxil@interserv.com.tw",
      maintainer="MaxiL",
      maintainer_email="maxil@interserv.com.tw",
      url="",
      download_url="https://github.com/maxi119/pylookwhat.git",
      packages=["pylookwhat"],
      install_requires=[],
      classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Programming Language :: Python",
        "Topic :: Utilities",    
        "Topic :: Software Development :: Libraries :: Python Modules",
        ])

