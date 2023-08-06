# coding=utf-8
"""
appinstance
erik@a8.nl (04-03-15)
license: GNU-GPL2
"""
from setuptools import setup
setup(name='unittester',
      version='0.3',
      description='Run python unit-tests as command-line applications (class and method based).',
      url='https://github.com/erikdejonge/unittester',
      author='Erik de Jonge',
      author_email='erik@a8.nl',
      license='GPL',
      packages=['unittester'],
      zip_safe=True, requires=['pyprofiler'])
