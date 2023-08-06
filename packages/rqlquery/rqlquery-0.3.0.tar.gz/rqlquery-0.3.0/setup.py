#!/usr/bin/env python
# pylint: disable-msg=W0404,W0622,W0704,W0613,W0152
# copyright 2014 UNLISH S.A.S. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of rqlquery.
#
# rqlquery is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# rqlquery is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with rqlquery. If not, see <http://www.gnu.org/licenses/>.
"""Generic Setup script, takes package info from __pkginfo__.py file.

"""
__docformat__ = "restructuredtext en"

import os

try:
    if os.environ.get('NO_SETUPTOOLS'):
        raise ImportError()  # do as there is no setuptools
    from setuptools import setup
    use_setuptools = True
except ImportError:
    from distutils.core import setup
    use_setuptools = False

# import required features
pkginfo = {}
with open('__pkginfo__.py', 'r') as f:
    exec(f.read(), pkginfo)

kwargs = {}
if use_setuptools:
    kwargs['install_requires'] = pkginfo['__depends__']

setup(
    name=pkginfo['distname'],
    version=pkginfo['version'],
    license=pkginfo['license'],
    description=pkginfo['short_desc'],
    long_description=pkginfo['long_desc'],
    author=pkginfo['author'],
    author_email=pkginfo['author_email'],
    url=pkginfo['web'],
    packages=[pkginfo['modname']],
    **kwargs)
