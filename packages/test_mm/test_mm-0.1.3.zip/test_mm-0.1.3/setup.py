# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 11:52:31 2015

@author: Magerl_4
"""

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name = 'test_mm',
      version = '0.1.3',
      description = 'PyPI tutorial.',
      long_description = 'Tutorial for making politically correct \
                              Python packages.',
      classifiers = [
        'Development Status :: 1 - Planning',
        'License :: Free For Home Use',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education :: Testing'
      ],
      keywords = 'test tutorial',
      url = 'https://mmagerl@bitbucket.org/mmagerl/packaging_tutorial.git',
      author = 'mmagerl',
      author_email = 'mmagerl@example.com',
      license = 'MM',
      packages = ['test_mm'],
      install_requires = [
            'markdown',
      ],
      include_package_data = True,
      zip_safe = False,
      test_suite = 'nose.collector',
      tests_require = ['nose'],)