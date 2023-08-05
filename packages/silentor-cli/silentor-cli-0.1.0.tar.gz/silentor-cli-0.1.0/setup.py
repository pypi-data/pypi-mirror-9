#!usr/bin/env python
#coding=utf-8
from setuptools import setup, find_packages
import silentorcli


setup(
    name='silentor-cli',
    author='Jayin Ton',
    author_email='tonjayin@gmail.com',
    version=silentorcli.__version__,
    url='http://github.com/jayin/silentorcli-cli',
    packages=find_packages(),
    description='the command line interface for silentor',
    long_description=open('README.md').read(),
    install_requires=[
        'click',
        'requests',
        'path.py'
    ],
    entry_points={
        'console_scripts': [
            'silentor = silentorcli.cli:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
)
