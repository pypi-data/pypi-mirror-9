#!/usr/bin/env python

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='podhub.meh',
    version='0.0.1',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['podhub'],
    include_package_data=True,
    license='BSD 3-Clause License',
    description='Flask framework with defaults.',
    long_description=README,
    url='https://github.com/podhub/meh',
    author='Jon Chen',
    author_email='bsd@voltaire.sh',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[
        'Flask==0.10.1',
    ],
)
