#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fs import __version__
from setuptools import setup, find_packages


INSTALL_REQUIRES = [
    'Twisted>=12.0.0',
    'argparse>=1.2.1',
    'certifi>=0.0.8',
    'chardet>=1.0.1',
    'wsgiref>=0.1.2',
    'zope.interface>=3.8.0',
]

setup(
    name='djeese-fs',
    version=__version__,
    description='A twisted based daemon file system.',
    author='Jonas Obrist',
    author_email='ojiidotch@gmail.com',
    url='https://github.com/aldryncore/djeese-fs',
    packages=find_packages(),
    license='Proprietary',
    platforms=['OS Independent'],
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    entry_points="""
    [console_scripts]
    djeesefs = fs.cli:main
    """,
)
