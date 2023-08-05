#! /usr/bin/env python

import os
import re
from setuptools import setup, find_packages


def get_version_from_init():
    file = open(os.path.join(
        os.path.dirname(__file__),
        'sigdispatch',
        '__init__.py'
    ))

    regexp = re.compile(r".*__version__ = '(.*?)'", re.S)
    version = regexp.match(file.read()).group(1)
    file.close()

    return version

setup(
    name='sigdispatch',
    version=get_version_from_init(),
    description='A simple events library.',
    author='Tyba',
    author_email='toni@tyba.com',
    url='http://github.com/Tyba/sigdispatch',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[],
)
