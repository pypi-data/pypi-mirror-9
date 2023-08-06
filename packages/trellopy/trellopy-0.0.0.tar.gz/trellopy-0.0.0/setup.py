#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
    'pymongo'
]

test_requirements = [
    # TODO: put package test requirements here
    'nose'
]

setup(
    name='trellopy',
    version='0.0.0',
    description="A Python mockup of Trello with CLI",
    long_description=readme + '\n\n' + history,
    author="Amol Mundayoor",
    author_email='amol.com@gmail.com',
    url='https://github.com/mund/trellopy',
    packages=[
        'trellopy',
    ],
    package_dir={'trellopy':
                 'trellopy'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='trellopy',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='nosetest',
    tests_require=test_requirements
)
