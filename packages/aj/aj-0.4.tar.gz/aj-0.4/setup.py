#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

import os
import aj

__requires = filter(None, open('requirements.txt').read().splitlines())


setup(
    name='aj',
    version=aj.__version__,
    install_requires=__requires,
    description='Web UI base toolkit',
    author='Eugene Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    packages=find_packages(),
)
