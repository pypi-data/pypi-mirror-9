#!/usr/bin/python -W default
#
# Copyright (c) 2013,2014,2015 Russell Stuart.
# Licensed under GPLv2, or any later version.
#
from distutils.core import setup
import re

def get_long_description():
  handle = open("doc/lrparsing.rst")
  while not next(handle).startswith("====="):
    pass
  long_description=[]
  for line in handle:
    if line.startswith("====="):
      break
    line = re.sub(":[a-z]*:`([^`<]*[^`< ])[^`]*`", "\\1", line)
    long_description.append(line)
  return ''.join(long_description[:-1])

setup(
    name="lrparsing",
    description="An LR(1) parser hiding behind a pythonic interface",
    long_description=get_long_description(),
    version="1.0.11",
    author="Russell Stuart",
    author_email="russell-lrparsing@stuart.id.au",
    url="http://lrparsing.sourceforge.net/",
    package_dir={"": "lrparsing"},
    py_modules=["lrparsing"],
    classifiers=[
	  "Development Status :: 4 - Beta",
	  "Intended Audience :: Developers",
	  "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
	  "Natural Language :: English",
	  "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
	  "Topic :: Software Development :: Libraries :: Python Modules",
      ]
)
