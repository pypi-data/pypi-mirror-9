#!/usr/bin/env python

from setuptools import setup, find_packages

import os

requires = [
    'six>=1.8.0,<2.0.0',
    'botocore==0.81.0',
    'python-dateutil>=2.1,<3.0.0']


setup(
    name='skew',
    version=open(os.path.join('skew', '_version')).read().strip(),
    description='A flat address space for all your AWS resources.',
    long_description=open('README.md').read(),
    author='Mitch Garnaat',
    author_email='mitch@garnaat.com',
    url='https://github.com/scopely-devops/skew',
    packages=find_packages(exclude=['tests*']),
    package_data={'skew': ['_version']},
    package_dir={'skew': 'skew'},
    install_requires=requires,
    license=open("LICENSE").read(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ),
)
