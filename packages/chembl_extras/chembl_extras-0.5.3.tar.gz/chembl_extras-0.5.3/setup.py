#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'mnowotka'

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='chembl_extras',
    version='0.5.3',
    author='Michal Nowotka',
    author_email='mnowotka@ebi.ac.uk',
    description='Python package providing extra collection of django custom management commands for use with ChEMBL and some classes for use in future',
    url='https://www.ebi.ac.uk/chembldb/index.php/ws',
    license='Apache Software License',
    packages=['chembl_extras',
              'chembl_extras.management',
              'chembl_extras.management.commands'],
    long_description=open('README.rst').read(),
    install_requires=[
        'chembl_business_model',
        'biopython',
        'clint>=0.3.3',
    ],
    include_package_data=False,
    classifiers=['Development Status :: 1 - Planning',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Scientific/Engineering :: Chemistry'],
    zip_safe=False,
)