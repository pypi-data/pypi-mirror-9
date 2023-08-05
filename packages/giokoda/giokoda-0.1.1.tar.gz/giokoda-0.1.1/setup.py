# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from giokoda import __version__ as version

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='giokoda',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    description='A utility for geocoding csv files.',
    long_description=README,
    author='Emil',
    author_email='emil@tehamalab.com',
    url='https://pypi.python.org/pypi/giokoda',
    download_url='https://github.com/WorldBank-Transport/giokoda/tarball/%s' %version,
    install_requires = ["geopy"],
    scripts=['geocode_csv'],
    license = 'Apache License, Version 2.0',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
