#!/usr/bin/python

from setuptools import setup

setup(name='pyscrambler',
      version='0.0.5',
      description='Concept data scrambler using permutations as a basis',
      url='https://github.com/saxbophone/pyscrambler',
      author='Joshua Saxby',
      author_email='joshua.a.saxby@gmail.com',
      license='MIT',
      packages=['pyscrambler', 'pyscrambler.permutations', 'pyscrambler.rearrange', 'pyscrambler.binary'],
      install_requires=['bitstring', 'nose'],
      zip_safe=False)
