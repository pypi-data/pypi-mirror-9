#!/usr/bin/env python

from setuptools import setup, find_packages, Command

# Get version from pkg index
from recon import __version__


desc = 'Recon is a Trigger-based replacement for RANCID.'

setup(
    name='recon',
    version=__version__,
    author='Jathan McCollum',
    author_email='jathan@gmail.com',
    packages=find_packages(exclude=['tests']),
    package_data={
        'twisted': ['plugins/trigger_xmlrpc.py'],
    },
    license='BSD',
    url='https://github.com/trigger/trigger',
    description=desc,
)
