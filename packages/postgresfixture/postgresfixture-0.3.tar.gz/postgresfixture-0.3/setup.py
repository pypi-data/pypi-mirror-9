#!/usr/bin/env python
# Copyright 2012-2014 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Distutils installer for postgresfixture."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type

import codecs
from sys import version_info

from setuptools import setup


with codecs.open("requirements.txt", "rb", encoding="utf-8") as fd:
    requirements = {line.strip() for line in fd}


setup(
    name='postgresfixture',
    version="0.3",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    packages={
        b'postgresfixture' if version_info.major == 2 else 'postgresfixture',
    },
    package_dir={'postgresfixture': 'postgresfixture'},
    install_requires=requirements,
    tests_require={"testtools >= 0.9.14"},
    test_suite="postgresfixture.tests",
    include_package_data=True,
    zip_safe=False,
    description=(
        "A fixture for creating PostgreSQL clusters and databases, and "
        "tearing them down again, intended for use during development "
        "and testing."),
    entry_points={
        "console_scripts": [
            "postgresfixture = postgresfixture.main:main",
            ],
        },
    )
