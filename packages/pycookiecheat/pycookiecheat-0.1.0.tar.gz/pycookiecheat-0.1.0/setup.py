#! /usr/bin/env python3
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import pypandoc

def md_to_rst(infile):
    return pypandoc.convert(infile, 'rst')

readme = md_to_rst('README.md')
history = md_to_rst('HISTORY.md')

requirements = [
        # TODO: Add any additional requirements for all templates
]

test_requirements = [
    'pytest>=2.6.4'
]

setup(
    name='pycookiecheat',
    version='0.1.0',
    description="Borrow cookies from your browser's authenticated session for use in Python scripts.",
    long_description=readme + '\n\n' + history,
    author='Nathan Henrie',
    author_email='nate@n8henrie.com',
    url='https://github.com/n8henrie/pycookiecheat',
    packages=[
        'pycookiecheat',
    ],
    package_dir={'pycookiecheat':
                 'pycookiecheat'},
    include_package_data=True,
    install_requires=requirements,
    license="GPLv3",
    zip_safe=False,
    keywords='pycookiecheat',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
