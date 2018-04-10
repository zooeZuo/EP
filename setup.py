#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# date        :2018/1/
# discriptions :
# vision      :
# copyright   :All copyright reserved by FMSH company
__author__ = 'zuodengbo'
from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

readme_rst = path.join(here,'README.rst')

if path.isfile(readme_rst):
    with open(readme_rst,encoding='utf-8') as f:
        description = f.read()

else:
    description = ''

version = {}
with open(path.join(here,'EP','__init__.py')) as fp:
    exec(fp.read(),version)

setup(
    name = 'EP',
    version = version['__version__'],
    description = description,
    license = 'FMSH',
    author = 'zuodengbo',
    url = '',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: FMSH Lisense',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    keywords = 'smartcard EP payment',

    packages = ['EP','EP.apdu_scripts','EP.card_service','EP.sign'],
    install_requires = ['random','pyscard','enum', 'six', 'requests', 'pycountry', 'Crypto', 'django'],
    entry_points = {
        'console_scripts':{
            'EPtool = EP.mock.client:run'
        }
    }
)