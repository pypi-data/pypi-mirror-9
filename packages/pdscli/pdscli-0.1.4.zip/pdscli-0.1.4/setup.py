#!/usr/bin/env python

from setuptools import setup, find_packages

import pdscli

requires = ['requests>=2.4.1', 'enum34']

setup_options = dict(
    name='pdscli',
    version=pdscli.__version__,
    description='Command Line Environment for the Personal Data Store.',
    long_description=open('README.rst').read(),
    author='Sean Fitts',
    author_email='sean@you.tc',
    url='http://youtechnology.github.io/pdsServer/doc/commandLine/',
    scripts=['bin/pds', 'bin/pds.cmd'],
    packages=find_packages('.', exclude=['tests*']),
    package_dir={'pdscli': 'pdscli'},
    package_data={'pdscli': ['examples/*']},
    include_package_data=True,
    install_requires=requires,
    license="Apache License 2.0",
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)

setup(**setup_options)