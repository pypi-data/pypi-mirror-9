# -*- coding: utf-8 -*-

# setup.py
# Part of ‘python-daemon’, an implementation of PEP 3143.
#
# Copyright © 2008–2015 Ben Finney <ben+python@benfinney.id.au>
# Copyright © 2008 Robert Niederreiter, Jens Klein
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 3 of that license or any later version.
# No warranty expressed or implied. See the file ‘LICENSE.GPL-3’ for details.

""" Distribution setup for ‘python-daemon’ library.
    """

from __future__ import (absolute_import, unicode_literals)

import sys
import os
import os.path
import pydoc
import distutils.util

from setuptools import (setup, find_packages)

import version


fromlist_expects_type = str
if sys.version_info < (3, 0):
    fromlist_expects_type = bytes


distribution_name = "python-daemon"
main_module_name = 'daemon'
main_module_fromlist = list(map(fromlist_expects_type, [
        '_metadata']))
main_module = __import__(
        main_module_name,
        level=0, fromlist=main_module_fromlist)
metadata = main_module._metadata

synopsis, long_description = pydoc.splitdoc(
        pydoc.getdoc(main_module))


version_info_filename = "version_info.json"
changelog_filename = "ChangeLog"

setup_dir = os.path.dirname(__file__)
changelog_filepath = distutils.util.convert_path(
        os.path.join(setup_dir, changelog_filename))

version_info = version.generate_version_info_from_changelog(changelog_filepath)
version_string = version_info['version']


(maintainer_name, maintainer_email) = version.parse_person_field(
        version_info['maintainer'])


setup(
        name=distribution_name,
        version=version_string,
        py_modules=['version'],
        packages=find_packages(exclude=["test"]),

        # Setuptools metadata.
        release_date=version_info['release_date'],
        maintainer=maintainer_name,
        maintainer_email=maintainer_email,
        zip_safe=False,
        test_suite="unittest2.collector",
        tests_require=[
            "unittest2",
            "testtools",
            "testscenarios >=0.4",
            "mock >=1.0",
            ],
        install_requires=[
            "setuptools",
            "lockfile >=0.10",
            ],
        entry_points={
            "distutils.setup_keywords": [
                "release_date = version:validate_distutils_release_date_value",
                ],
            "egg_info.writers": [
                "{filename} = version:generate_egg_info_metadata".format(
                    filename=version_info_filename),
                ],
            },

        # PyPI metadata.
        author=metadata.author_name,
        author_email=metadata.author_email,
        description=synopsis,
        license=metadata.license,
        keywords="daemon fork unix".split(),
        url=metadata.url,
        long_description=long_description,
        classifiers=[
            # Reference: http://pypi.python.org/pypi?%3Aaction=list_classifiers
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        )


# Local variables:
# coding: utf-8
# mode: python
# End:
# vim: fileencoding=utf-8 filetype=python :
