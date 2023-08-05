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
    name='chembl_migration_model',
    version='0.5.7',
    author='Michal Nowotka',
    author_email='mnowotka@ebi.ac.uk',
    description='Core ChEMBL python ORM model for data exports and migration',
    url='https://www.ebi.ac.uk/chembl/',
    license='Apache Software License',
    packages=['chembl_migration_model'],
    long_description=open('README.rst').read(),
    install_requires=[
        'chembl_core_model>=0.5.10'
    ],
    include_package_data=False,
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Scientific/Engineering :: Chemistry'],
    zip_safe=False,
)
