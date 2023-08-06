#!/usr/bin/env python3

from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

import os
import numpy

ext_modules = []
cmd_class = {}

setup(
    name = 'camoco',
    version = '0.1.3',
    packages = find_packages(),
    scripts = [],

    install_requires = [
        'cython>=0.16',    
        'apsw>=3.8',
        'igraph>=0.1.5',
        'matplotlib>=1.4.3',
        'numpy>=1.9.1',
        'pandas>=0.15',
        'scipy>=0.15',
        'termcolor>=1.1.0'
    ],

    package_data = {
        '':['*.cyx']    
    },
    include_package_data=True,

    author = 'Rob Schaefer',
    author_email = 'schae234@gmail.com',
    description = 'Library for Co-Analysis of Molecular Componenets.',
    license = "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License",
    url = 'https://github.com/schae234/camoco',

    ext_modules=ext_modules,
    include_dirs=[numpy.get_include()]

)
