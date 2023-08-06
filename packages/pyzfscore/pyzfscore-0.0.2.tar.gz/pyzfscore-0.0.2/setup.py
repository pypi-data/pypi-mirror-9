#! /usr/bin/env python
"""
Part of PyZFSCore.

Copyright 2013 Trevor Joynson

"""
from setuptools import setup

import pyzfscore
import pyzfscore.libzfs
import pyzfscore.libnvpair

setup(
    name='pyzfscore',
    version='0.0.2',
    description='ZFS CFFI wrapper.',
    license='GPL3',
    author='Trevor Joynson',
    author_email='github@skywww.net',
    maintainer='Ben Cole',
    maintainer_email='wengole@gmail.com',
    url='http://github.com/wengole/pyzfscore',
    packages=[
        'pyzfscore',
        'pyzfscore.libzfs',
        'pyzfscore.flufl',
        'pyzfscore.flufl.enum',
    ],
    zip_safe=False,
    ext_modules=[
        pyzfscore.libzfs.ffi.verifier.get_extension(),
        pyzfscore.libnvpair.ffi.verifier.get_extension(),
    ],
)
