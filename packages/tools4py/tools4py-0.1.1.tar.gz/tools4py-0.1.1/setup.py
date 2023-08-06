import os
import numpy
from setuptools import find_packages
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

version = '0.1.1'
README = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = open(README).read() + '\n'

setup(name='tools4py',
      version=version,
      description=("Tools. For Python."),
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
          ("Topic :: Software Development :: Libraries :: Python Modules"),
      ],
      keywords=[''],
      author='Samuel Skillman',
      author_email='samskillman@gmail.com',
      license='MIT',
      url="https://bitbucket.org/samskillman/tools4py",
      packages=find_packages(),
      install_requires = ['mpi4py'],
      )

