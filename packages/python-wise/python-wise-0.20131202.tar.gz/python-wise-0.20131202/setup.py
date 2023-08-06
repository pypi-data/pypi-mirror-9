#!/usr/bin/python
# -*- mode: python; coding: utf-8 -*-

from distutils.core import setup

setup(name = 'python-wise',
      version = '0.20131202',
      description = 'Web distributed objects',
      packages = ['wise'],
      package_data = {'wise': ['js/*']},
      install_requires = ['commodity', 'tornado'],
      url              = 'https://bitbucket.org/arco_group/wise',
      maintainer       = 'ARCO Group',
      maintainer_email = 'arco.uclm@gmail.com',
      license          = 'GPLv3',
      )
