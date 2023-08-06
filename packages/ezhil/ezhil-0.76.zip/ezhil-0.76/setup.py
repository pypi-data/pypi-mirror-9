#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# (C) 2008-2015 முத்தையா அண்ணாமலை 
# ezhil language project

try:
    # specify dependecies properly
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from codecs import open

setup(name='ezhil',
      version='0.76',
      description='Ezhil - Tamil programming language implemented in Python',
      author='Muthiah Annamalai',
      author_email='ezhillang@gmail.com',
      url='https://github.com/arcturusannamalai/Ezhil-Lang',
      packages=['ezhil'],
      license='GPLv3',
      platforms='PC,Linux,Mac',
      classifiers='Natural Language :: Tamil',
      install_requires = ["open-tamil","argparse"],
      long_description='Ezhil is a Tamil programming language for early education',#open('README.md','r','UTF-8').read()
      download_url='https://github.com/arcturusannamalai/Ezhil-Lang/archive/latest.zip',#pip
      )
