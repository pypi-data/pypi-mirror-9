#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

README = open('README.md').read()
VERSION = open("django_pgjsonb/VERSION").read()

setup(
    name='django-pgjsonb',
    version=VERSION,
    description='Django Postgres JSONB Fields support with lookups',
    long_description=README,
    author='Jay Young(yjmade)',
    author_email='dev@yjmade.net',
    packages=find_packages(),
    install_requires=['Django>=1.7','psycopg2>=2.5.4'],
    package_data={'django_pgjsonb': ['VERSION']},
    include_package_data=True,
)
