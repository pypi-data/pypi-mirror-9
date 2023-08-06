#!/usr/bin/env python
# coding: utf-8
from setuptools import find_packages, setup

with open('README.rst') as f:
    long_description = f.read()


setup(
    author='juknsh',
    author_email='juknsh@gmail.com',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
    description='Django Dict Response',
    install_requires=['Django>=1.7'],
    keywords='python django',
    long_description=long_description,
    name='django-dict-response',
    packages=find_packages(),
    url='https://github.com/juknsh/django-dict-response',
    version='0.0.7',
)
