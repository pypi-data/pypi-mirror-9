'''
Created on 5 Dec 2013

@author: Akul Mathur
'''

from distutils.core import setup

from setuptools import find_packages

import flatten


def readme():
    with open('README.txt') as f:
        open_readme = f.read()
        f.close()
    return open_readme

setup(name='FlattenList',
      version=flatten.__version__,
      description='Given a list of nested lists/tuples, returns all the elements in a single list',
      url='https://pypi.python.org/pypi/FlattenList',
      author=flatten.__author__,
      author_email=flatten.__author_email__,
      classifiers=flatten.__classifiers__,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      scripts=[],
      install_requires=[])
