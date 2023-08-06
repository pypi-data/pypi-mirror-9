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
    'click'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='dupes',
    version='0.1.0',
    description="Identify duplicate files (by SHA1) and remove them if needed",
    long_description=readme + '\n\n' + history,
    author="Devin Kelly",
    author_email='dwwkelly@fastmail.fm',
    url='https://github.com/dwwkelly/dupes',
    packages=[
        'dupes',
    ],
    package_dir={'dupes':
                 'dupes'},
    include_package_data=True,
    install_requires=requirements,
    license="GPL2",
    zip_safe=False,
    scripts=['scripts/dupes'],
    keywords='dupes',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL2 License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
