#!/usr/bin/env python
from setuptools import setup

version = '0.4'

setup(
    name='adblockparser',
    version=version,
    description="Parser for Adblock Plus rules",
    long_description=open('README.rst').read() + '\n\n' + open('CHANGES.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    keywords='adblock easylist',
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',
    url='https://github.com/scrapinghub/adblockparser',
    license='MIT',
    packages=['adblockparser'],
)
