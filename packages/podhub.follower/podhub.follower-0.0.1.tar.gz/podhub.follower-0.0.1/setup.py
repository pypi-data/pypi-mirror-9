#!/usr/bin/env python3

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='podhub.follower',
    version='v0.0.1',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['podhub'],
    include_package_data=True,
    license='BSD 3-Clause License',
    description='RSS client for PodHub',
    long_description=README,
    url='https://github.com/podhub/follower',
    author='Jon Chen',
    author_email='bsd@voltaire.sh',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=[
        'feedparser==5.1.3',
        'Flask==0.10.1',
        'pylibmc==1.4.1',
    ],
    scripts=[
        'scripts/follower'
    ]
)
