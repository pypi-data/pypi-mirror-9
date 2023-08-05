#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Denis Rogov'

from setuptools import setup

setup(
    name='hipchat_notif',
    url='https://bitbucket.org/rodevl/hipchat_notif',
    download_url='https://bitbucket.org/rodevl/hipchat_notif/get/0.2.3.zip',
    py_modules=['hipchat_notif'],
    version='0.2.3',
    packages = ['hipchat_notif'],
    install_requires=['requests>=2.3.0'],
    author=__author__,
    author_email='rogovdv@gmail.com',
    keywords=["HipChat", "HipChat Client"],
    license='MIT',
    description = "Simple Python library for the HipChat API v1",
    long_description=open('README.md').read(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications :: Chat"
    ]
)
