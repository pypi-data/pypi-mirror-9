#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import multipleformwizard


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = multipleformwizard.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-multipleformwizard',
    version=version,
    description="""An extension to the official Django form wizard supporting multiple forms on a wizard step.""",
    long_description=readme + '\n\n' + history,
    author='Dirk Moors',
    author_email='dirkmoors@gmail.com',
    url='https://github.com/vikingco/django-multipleformwizard',
    packages=[
        'multipleformwizard',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=1.6',
        'six>=1.9.0'
    ],
    license="MIT",
    zip_safe=False,
    keywords='django-multipleformwizard',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
