#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


setup(
    name='mprofi_api_client',
    version='0.1.0',
    description='Python Client library for mProfi REST API',
    long_description=readme + '\n\n' + history,
    author='Materna Communications Sp. z o.o.',
    author_email='pomoc@materna.com.pl',
    url='https://github.com/materna/mprofi_api_client_python',
    packages=[
        'mprofi_api_client',
    ],
    package_dir={'mprofi_api_client':
                 'mprofi_api_client'},
    include_package_data=True,
    install_requires=[],
    license="Apache",
    zip_safe=False,
    keywords=['mprofi', 'api', 'client'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
)
