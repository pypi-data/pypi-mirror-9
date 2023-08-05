#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='rivr-jinja',
    version='0.1.0',
    description='rivr integration for using the Jinja template engine.',
    url='https://github.com/rivrproject/rivr-jinja',
    packages=find_packages(),
    install_requires=[
        'rivr',
        'Jinja2'
    ],
    author='Kyle Fuller',
    author_email='inbox@kylefuller.co.uk',
    license='BSD',
    classifiers=(
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'License :: OSI Approved :: BSD License',
    )
)

