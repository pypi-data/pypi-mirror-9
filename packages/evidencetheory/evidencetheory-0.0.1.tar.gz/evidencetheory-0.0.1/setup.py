#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jonathan S. Prieto
# @Date:   2015-03-03 15:56:45
# @Last Modified by:   Jonathan Prieto 
# @Last Modified time: 2015-03-03 16:41:18

VERSION = "0.0.1"

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
    name='evidencetheory',
    packages=find_packages(),
    version=VERSION,
    include_package_data=True,
    license='MIT',
    description='Evidence Theory',
    author='Jonathan S. Prieto',
    author_email='prieto.jona@gmail.com',
    url='https://github.com/d555/evidencetheory',   # use the URL to the github repo
    download_url='https://github.com/d555/evidencetheory/',
    # arbitrary keywords
    keywords='evidencetheory dempster shafer fusion information',
    long_description=open('README.rst').read(),
    zip_safe=True,
    classifiers=[
        'Intended Audience :: Information Technology',
    ],
)

# pandoc --from=markdown_github --to=rst --output=README.rst README.md
# Pasos para subir a pypi
# git tag v...
# python setup.py register -r pypi
# python setup.py sdist upload -r pypi
