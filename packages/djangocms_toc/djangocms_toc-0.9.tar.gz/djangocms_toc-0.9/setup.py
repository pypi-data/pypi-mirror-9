#!/usr/bin/env python
#
# Copyright (C) 2015  Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import setup

from djangocms_toc import __version__, __pkgname__

setup(
    name         = __pkgname__,
    version      = __version__,
    description  = 'Table of Contents Plugin for django CMS',
    author       = 'Martin Owens',
    author_email = 'doctormo@gmail.com',
    url          = 'None',
    packages     = ('djangocms_toc', 'djangocms_toc.templatetags'),
    license      = 'AGPLv3',
    include_package_data=True,
)
