#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

from pip.req import parse_requirements

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'requests',
    'pytz',
    'python-dateutil',
]

test_requirements = requirements.extend([
    'mock',
    'magicmock',
])

setup(
    name='exreporter',
    version='0.1.3',
    description='Report Internal Server Errors as Issues',
    long_description=readme + '\n\n' + history,
    author='Vedarth Kulkarni',
    author_email='vedarthk@vedarthz.in',
    url='https://github.com/vedarthk/exreporter',
    packages=find_packages(),
    package_dir={'exreporter':
                 'exreporter'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='exreporter',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
