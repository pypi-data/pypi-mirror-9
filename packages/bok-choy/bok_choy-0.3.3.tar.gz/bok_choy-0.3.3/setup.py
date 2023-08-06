#!/usr/bin/env python

from setuptools import setup

VERSION = '0.3.3'
DESCRIPTION = 'UI-level acceptance test framework'
REQUIREMENTS = [
    line.strip() for line in open("requirements.txt").readlines()
]

setup(
    name='bok_choy',
    version=VERSION,
    author='edX',
    url='http://github.com/edx/bok-choy',
    description=DESCRIPTION,
    license='Apache 2.0',
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Apache Software License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Testing',
                 'Topic :: Software Development :: Quality Assurance'],
    packages=['bok_choy'],
    install_requires=REQUIREMENTS,
)
