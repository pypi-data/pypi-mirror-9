#!/usr/bin/env python

import sys
from setuptools import setup

required_packages = ['pyparsing==2.0.3']
if sys.version_info[:2] == (2, 6):
    required_packages.append('ordereddict')

setup(
    name='pyhocon',
    version='0.2.4',
    description='HOCON parser for Python',
    long_description='pyhocon is a HOCON parser for Python. Additionally we provide a tool (pyhocon) to convert any HOCON content into json, yaml and properties format.',
    keywords='hocon parser',
    license='Apache License 2.0',
    author="Francois Dang Ngoc",
    author_email='francois.dangngoc@gmail.com',
    url='http://github.com/chimpler/pyhocon/',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[
        'pyhocon',
    ],
    install_requires=required_packages,
    entry_points={
        'console_scripts': [
            'pyhocon=pyhocon.tool:main'
        ]
    }
)
