#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='pyremotevbox',
    version='0.1.0',
    description='Python API to talk to a remote VirtualBox using VirtualBox WebService',
    long_description=readme + '\n\n' + history,
    author='Ramakrishnan G',
    author_email='rameshg87@gmail.com',
    url='https://github.com/rameshg87/pyremotevbox',
    packages=[
        'pyremotevbox',
    ],
    package_dir={'pyremotevbox':
                 'pyremotevbox'},
    include_package_data=True,
    license="Apache",
    zip_safe=False,
    keywords='pyremotevbox',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
    ],
)
