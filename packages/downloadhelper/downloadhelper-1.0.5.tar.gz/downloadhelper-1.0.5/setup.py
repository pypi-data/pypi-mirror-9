#!/usr/bin/env python
# coding=utf-8
import os
import sys

import downloadhelper

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'downloadhelper',
]

requires = [
    'requests',
]

try:
    with open('README.rst', 'r') as f:
        readme = f.read()
except :
    readme = ''
try:
    with open('HISTORY.rst', 'r') as f:
        history = f.read()
except :
    history = ''

setup(
    name='downloadhelper',
    version=downloadhelper.VERSION,
    description='Python Download Helper',
    long_description=readme + '\n\n' + history,
    author='Cole Smith',
    author_email='uniquecolesmith@gmail.com',
    url='',
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE'], 'downloadhelper': ['*.pem']},
    package_dir={'downloadhelper': 'downloadhelper'},
    include_package_data=True,
    install_requires=requires,
    license='Apache 2.0',
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ),
    extras_require={
        'secuirity': ['pyOpenSSL', 'ndg-httpsclient', 'pyasn1'],
    },
)
