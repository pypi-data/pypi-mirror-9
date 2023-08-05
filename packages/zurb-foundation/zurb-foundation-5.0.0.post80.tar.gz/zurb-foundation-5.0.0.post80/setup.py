#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup
import imp
import glob

here = os.path.dirname(os.path.abspath(__file__))
zurb_pkg = "zurb_foundation"

version = imp.load_source(zurb_pkg, os.path.join(here, '__init__.py')).__version__

here = os.path.dirname(__file__)
f = open(os.path.join(here, "README.rst"), "rt")
readme = f.read()
f.close()

setup(
    name='zurb-foundation',
    version=version,
    description='The most advanced responsive front-end framework in the world. Quickly create prototypes and production code for sites and apps that work on any kind of device',
    long_description=readme,
    author='ZURB Inc.',
    author_email = "foundation@zurb.com",
    maintainer = "Arkadiusz Dzięgiel",
    maintainer_email = "arkadiusz.dziegiel@glorpen.pl",
    url='http://foundation.zurb.com',
    packages=[zurb_pkg],
    package_dir={zurb_pkg:"."},
    package_data={zurb_pkg: list(glob.glob("scss/*.*"))+list(glob.glob("scss/*/*.*"))+list(glob.glob("scss/*/*/*.*"))+list(glob.glob("css/*.*"))+list(glob.glob("js/*.*"))+list(glob.glob("js/*/*.*"))},
    include_package_data = True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
    ]
)
