#!/usr/bin/env python
# coding=utf-8

import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'CHANGELOG.rst')).read()

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
zip_safe = not on_rtd

version = '1.2'

setup(
    name='test-service',
    version=version,
    description="test-service is a Python package that test web service base on linux curl.",
    long_description=README + '\n\n' + NEWS,
    install_requires=['six', 'django'],
    license='MIT License',
    author='kylinfish',
    author_email='kylinfish@126.com',
    keywords='test-service',
    url='https://bitbucket.org/kylinfish/test-service',
    packages=find_packages(),
    include_package_data=True,
    platforms=["any"],
    zip_safe=zip_safe,
    classifiers=[
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License'
    ]
)