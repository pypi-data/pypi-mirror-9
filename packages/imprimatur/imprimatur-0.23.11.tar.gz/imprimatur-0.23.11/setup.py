#!/usr/bin/env python

import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'imprimatur/_version.py'
versioneer.versionfile_build = 'imprimatur/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'imprimatur-'
from setuptools import setup

long_description = """\

Imprimatur
----------

Imprimatur is a tool for performing automated functional testing on web
applications. The tests are described in a simple test script. Along with the
standard HTTP methods, Imprimatur handles authentication, file uploads and
HTTPS. The responses are validated using regular expressions."""

cmdclass = dict(versioneer.get_cmdclass())

version = versioneer.get_version()

setup(
    name="imprimatur",
    version=version,
    cmdclass=cmdclass,
    description="Functional testing tool for web applications.",
    long_description=long_description,
    author="Tony Locke",
    author_email="tlocke@tlocke.org.uk",
    url="https://github.com/tlocke/imprimatur",
    license="GPL",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
    keywords="functional testing web",
    packages=("imprimatur",),
    install_requires=['requests>=2.5.1', 'flask', 'argparse', 'six'],
    entry_points={'console_scripts': ['imprimatur = imprimatur.console:main']}
)
