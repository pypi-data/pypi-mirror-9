#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='MapGitConfig',
    packages=['gitconfig'],
    version=1.1,
    description='Git Config Wrapper',
    author='Zalando',
    author_email='joao.santos@zalando.de',
    url='https://github.com/zalando/python-gitconfig',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Version Control',
    ],
    long_description="MapGitConfig is a small wrapper around the git cli to expose git configuration as a mapping."
)

