# -*- coding: utf-8 -*-
# Copyright 2015 Tencent
# Author: Joe Lei <thezero12@hotmail.com>
import setuptools
import sys

if sys.platform.startswith("win"):
    scripts = ['bin/autowatchme.pyw']
else:
    scripts = []

setuptools.setup(
    scripts=scripts,
    setup_requires=['pbr'],
    pbr=True
)
