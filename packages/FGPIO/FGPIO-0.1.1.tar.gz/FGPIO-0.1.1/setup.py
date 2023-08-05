#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages

import FGPIO
 
setup(
    name='FGPIO',
    version=FGPIO.__version__,
    packages=find_packages(),
    author="FredThx",
    author_email="FredThx@gmail.com",
    description="Gestion des E/S d'un Raspberry PI ou d'un pcduino",
    long_description=open('README.md').read(),
    install_requires=["smbus-cffi >= 0.4.1"],
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
    # entry_points = {
        # 'console_scripts': [
            # 'proclame-sm = sm_lib.core:proclamer',
        # ],
    # },
    license="WTFPL",

)