# coding=utf-8
"""
appinstance
Active8 (04-03-15)
license: GNU-GPL2
"""

from setuptools import setup
setup(name='unittester',
      version='22',
      description='Run python unit-tests as command-line applications (class and method based).',
      url='https://github.com/erikdejonge/unittester',
      author='Erik de Jonge',
      author_email='erik@a8.nl',
      license='GPL',
      packages=['unittester'],
      zip_safe=True,
      install_requires=['consoleprinter', 'pyprofiler'],
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Development Status :: 4 - Beta ",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Operating System :: POSIX",
          "Topic :: Software Development :: Quality Assurance",
          "Topic :: Software Development :: Testing",
          "Topic :: System",
      ])
