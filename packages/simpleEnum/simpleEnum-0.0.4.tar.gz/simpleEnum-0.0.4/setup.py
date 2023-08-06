# -*- coding: utf-8 -*-
#
# Copyright © 2015 Raul Ramos
# Licensed under the terms of the MIT License
# (see simpleEnum.py for details)
from setuptools import setup, find_packages

name   = 'simpleEnum'
module = __import__(name)

setup\
(
    name=name,
    version=module.__version__,
    description='simpleEnum - A really really simple Python enum class',
    author='Raul Ramos',
    author_email='galtza@wokki.me',
    url='https://github.com/galtza/simpleEnum',
    keywords= 'enum simple python',
    platforms=['any'],
    py_modules=['simpleEnum'],
    classifiers=\
    [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
