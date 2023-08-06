#!/usr/bin/env python3

from setuptools import setup, find_packages, Extension

pysmall = Extension('pysmall',
        sources = ['PCCUP.pyx','']
)

setup(
    name = 'camoco',
    version = '0.1.2',
    packages = find_packages(),
    scripts = [],

    install_requires = [],

    package_data = {
        '':['*.cyx']    
    },

    author = 'Rob Schaefer',
    author_email = 'schae234@gmail.com',
    description = 'Library for Co-Analysis of Molecular Componenets.',
    license = "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License",
    url = 'https://github.com/schae234/camoco',
)
