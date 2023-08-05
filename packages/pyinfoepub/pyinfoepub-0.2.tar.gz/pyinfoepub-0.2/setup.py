#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pyinfoepub',
    version='0.2',
    description='PyInfoEpub helps you retrieve specific information from an epub file.',
    long_description=readme + '\n\n' + history,
    author='Cristian Năvălici',
    author_email='cristian.navalici@gmail.com',
    url='https://github.com/cristianav/PyInfoEpub',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requirements,
    license="GPLv3",
    zip_safe=False,
    keywords='pyinfoepub',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)


# https://pypi.python.org/pypi?%3Aaction=list_classifiers
