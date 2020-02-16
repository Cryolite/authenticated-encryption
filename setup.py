#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name='authenticated-encryption',
    author='Cryolite',
    author_email='cryolite.indigo@gmail.com',
    description='Script performing authenticated encryption.',
    url='https://github.com/Cryolite/authenticated-encryption',
    scripts=['bin/authenticated-encryption'],
    version='0.0.1alpha0',
    install_requires=['pycrypto>=2.6.1'],
    packages=find_packages()
)
