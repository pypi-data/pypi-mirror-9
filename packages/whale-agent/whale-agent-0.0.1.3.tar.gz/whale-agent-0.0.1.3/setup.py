#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from whale_agent import AUTHOR, EMAIL, DESCRIPTION, VERSION, GIT, LICENSE, KEYWORDS

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'requests',
    'simplejson',
    'pytz',
    'pyaml'
]

test_requirements = [
    'pytest',
    'pytest-cov',
    'mock',
    'coverage',
]

setup(
    name='whale-agent',
    version=VERSION,
    description=DESCRIPTION,
    long_description=readme + '\n\n' + history,
    author=AUTHOR,
    author_email=EMAIL,
    url=GIT,
    packages=find_packages(exclude='tests'),
    include_package_data=True,
    install_requires=requirements,
    license=LICENSE,
    zip_safe=False,
    keywords=KEYWORDS,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        "console_scripts": ['whale = whale_agent.cli:main']
    },
    tests_require=test_requirements,
)
