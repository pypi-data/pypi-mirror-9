#!/usr/bin/env python
# This file is part of the vecnet.emod package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/vecnet.emod
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Note that vecnet is a namespace package.
# Please refer to https://pythonhosted.org/setuptools/setuptools.html#namespace-packages for additional details
#
# This implies that __init__.py in vecnet package MUST contain the line
# __import__('pkg_resources').declare_namespace(__name__)
# This code ensures that the namespace package machinery is operating and the current package is registered
# as a namespace package. You must NOT include any other code and data in a namespace packages's __init__.py

from setuptools import setup, find_packages

setup(
    name="vecnet.emod",
    version="0.5.0",
    license="MPL 2.0",
    author="University of Notre Dame, Center for Research Computing",
    author_email="khostetl@nd.edu",
    description="Python package for loading EMOD weather files, store the data in memory so that it can be modified, " +
                "and saves the data to weather files. Allows for conversions between nodeIDs and latitude and " +
                "longitude pairs.",
    keywords="weather data climate file malaria converter conversion node id nodeid latitude longitude",
    url="https://github.com/vecnet/vecnet.emod",
    packages=find_packages(),  # https://pythonhosted.org/setuptools/setuptools.html#using-find-packages
    #package_dir = {'': 'emod'},
    namespace_packages=['vecnet', ],
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
