#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages

import FAVRIP
 
setup(
    name='FAVRIP',
    version=FAVRIP.__version__,
    packages=find_packages(),
    author="FredThx",
    author_email="FredThx@gmail.com",
    description="Manage Audio Video Receiver via TCP-IP",
    long_description=open('README.md').read(),
    install_requires=[],
    include_package_data=True,
    url='',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7"
    ],
    license="WTFPL",

)