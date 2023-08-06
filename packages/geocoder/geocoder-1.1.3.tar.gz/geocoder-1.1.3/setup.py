#!/usr/bin/python
# coding: utf8
import sys
import os
from setuptools import setup

__version__ = '1.1.3'
install_requires = ['requests', 'ratelim']

setup(
    name='geocoder',
    version=__version__,
    description="A complete Python Geocoding module made easy.",
    long_description=open('README.md').read(),
    author='Denis Carriere',
    author_email='carriere.denis@gmail.com',
    url='https://github.com/DenisCarriere/geocoder',
    download_url='https://github.com/DenisCarriere/geocoder/tarball/master',
    license=open('LICENSE').read(),
    entry_points='''
        [console_scripts]
        geocode=geocoder.cli:cli
    ''',
    packages=['geocoder'],
    package_data={'': ['LICENSE', 'README.md']},
    package_dir={'geocoder': 'geocoder'},
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    keywords='geocoder arcgis tomtom opencage google bing here',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ),
)
