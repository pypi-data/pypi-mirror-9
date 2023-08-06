#!/usr/bin/env python

from setuptools import setup

setup(
    name="dom",
    version="0.7",
    description="An easy-to-use command line utility for domain name lookups.",
    author="Zach Williams",
    author_email="hey@zachwill.com",
    url="http://github.com/zachwill/dom",
    license="MIT",
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    packages=[
        "domainr"
    ],
    scripts=[
        "dom"
    ],
    tests_require=['mock'],
    install_requires=[
        "requests",
        "simplejson",
        "termcolor"
    ]
)
