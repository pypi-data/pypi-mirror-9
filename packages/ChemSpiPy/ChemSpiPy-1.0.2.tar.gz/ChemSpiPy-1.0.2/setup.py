#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup


if os.path.exists('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = '''A simple Python wrapper around the ChemSpider Web Services.'''

setup(
    name='ChemSpiPy',
    version='1.0.2',
    author='Matt Swain',
    author_email='m.swain@me.com',
    license='MIT',
    url='https://github.com/mcs07/ChemSpiPy',
    packages=['chemspipy'],
    description='A simple Python wrapper around the ChemSpider Web Services.',
    long_description=long_description,
    keywords='chemistry cheminformatics chemspider rsc rest api',
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=['requests', 'six'],
    tests_require=['nose'],
    extras_require={'lxml': ['lxml']},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
