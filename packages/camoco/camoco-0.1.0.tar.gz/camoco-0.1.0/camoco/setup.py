#!/usr/bin/env python3

from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = 'Cythonized PCC calculations',
    ext_modules = cythonize("PCCUP.pyx"),
)

#setup(name='Camoco',
#    version='0.1.0',
#    description='Library for creating and analyzing gene coexpression networks.',
#    author='Rob Schaefer',
#    author_email='schae234@gmail.com',
#    url='https://github.com/schae234/camoco',
#    packages=['camoco']
#)

