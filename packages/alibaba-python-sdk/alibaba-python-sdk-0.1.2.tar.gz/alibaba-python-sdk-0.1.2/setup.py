#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys

if float("%d.%d" % sys.version_info[:2]) < 2.5 or float("%d.%d" % sys.version_info[:2]) >= 3.0:
    sys.stderr.write("Your Python version %d.%d.%d is not supported.\n" % sys.version_info[:3])
    sys.stderr.write("osscmd requires Python between 2.4 and 3.0.\n")
    sys.exit(1)

setup(
    name='alibaba-python-sdk',
    version='0.1.2',
    packages=['alibaba','alibaba.tmp'],
    license='GPL version 2',
    author='chenqiu',
    author_email='',
    description='Aibaba SDK for python.',
)
