# -*- coding: utf-8 -*-
'''
@author: saaj
'''


try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


setup(
  name             = 'PageCalc',
  version          = '0.2.2',
  author           = 'saaj',
  author_email     = 'mail@saaj.me',
  packages         = ['pagecalc'],
  package_data     = {'pagecalc' : ['example/*']},
  test_suite       = 'pagecalc.test',
  url              = 'https://bitbucket.org/saaj/pagecalc',
  license          = 'LGPL-2.1+',
  description      = 'Python pagination calculator',
  long_description = open('README.txt').read(),
  platforms        = ['Any'],
  classifiers      = [
    'Topic :: Software Development :: Libraries',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Intended Audience :: Developers'
  ]
)

