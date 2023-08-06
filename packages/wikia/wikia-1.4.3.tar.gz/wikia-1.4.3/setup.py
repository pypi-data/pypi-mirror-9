# -*- coding: utf-8 -*-
import codecs
import os
import re
import setuptools


def local_file(file):
  return codecs.open(
    os.path.join(os.path.dirname(__file__), file), 'r', 'utf-8'
  )

install_reqs = [
  line.strip()
  for line in local_file('requirements.txt').readlines()
  if line.strip() != ''
]

version = re.search(
  "^__version__ = \((\d+), (\d+), (\d+)\)$",
  local_file('wikia/__init__.py').read(),
  re.MULTILINE
).groups()


setuptools.setup(
  name = "wikia",
  version = '.'.join(version),
  author = "Preston Carpenter",
  author_email = "APragmaticPlace@gmail.com",
  description = "Wikia API for Python",
  license = "MIT",
  keywords = "python wikipedia API",
  url = "https://github.com/Timidger/Wikia",
  install_requires = install_reqs,
  packages = ['wikia'],
  long_description = local_file('README.rst').read(),
  classifiers = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3'
  ]
)
