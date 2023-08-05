#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='spur',
    version='0.3.13',
    description='Run commands and manipulate files locally or over SSH using the same interface',
    long_description=read("README.rst"),
    author='Michael Williamson',
    url='http://github.com/mwilliamson/spur.py',
    keywords="ssh shell subprocess process",
    packages=['spur'],
    install_requires=["paramiko>=1.13.1,<2"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
    ],
)
