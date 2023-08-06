#!/usr/bin/env python
import os
from setuptools import setup, find_packages

__doc__ = "Mixin for adding class-based views to ModelAdmin"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

readme = read('README.rst')
changelog = read('CHANGELOG.rst')

setup(
    name='django-adminextraviews',
    version='1.1.0',
    description=__doc__,
    long_description=readme + '\n\n' + changelog,
    author='Fusionbox, Inc.',
    author_email='programmers@fusionbox.com',
    url='https://github.com/fusionbox/django-adminextraviews',
    packages=[package for package in find_packages() if package.startswith('adminextraviews')],
    install_requires=[
        'Django>=1.4',
    ],
    test_suite='setuptest.setuptest.SetupTestSuite',
    tests_require=[
        'django-setuptest',
    ],
    license="Apache 2.0",
    zip_safe=True,
    keywords='django-adminextraviews',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
