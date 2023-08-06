#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    "appdirs"
]

test_requirements = [
]

# Copied from (and hacked):
# https://github.com/pypa/virtualenv/blob/develop/setup.py#L42
def get_version(filename):
    import re

    here = os.path.dirname(__file__)
    with open(os.path.join(here, filename)) as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)

setup(
    name='pyparadox',
    version=get_version(os.path.join("pyparadox", "__init__.py")),
    description="PyParadox is a nix launcher for Paradox titles.",
    long_description=readme + '\n\n' + history,
    author="Carmen Bianca Bakker",
    author_email='carmenbbakker@gmail.com',
    url='https://gitlab.com/carmenbbakker/pyparadox',
    packages=[
        'pyparadox',
    ],
    package_dir={'pyparadox': 'pyparadox'},
    entry_points={
        'gui_scripts': [
            'pyparadox-qt = pyparadox.main:main_gui'
        ],
        'console_scripts': [
            'pyparadox = pyparadox.main:main_console'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GPLv3+",
    zip_safe=False,
    keywords='pyparadox',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
