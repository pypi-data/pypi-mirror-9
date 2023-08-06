#!/usr/bin/env python

# Copyright (C) 2015 David Villa Alises
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


from distutils.core import setup

setup(name         = 'bucket',
      version      = '0.20150324',
      description  = 'Bitbucket from command line',
      author       = 'David Villa Alises',
      author_email = '<David.Villa@gmail.com>',
      url          = 'https://bitbucket.org/DavidVilla/bucket',
      license      = 'GPL v2 or later',
      scripts      = ['bin/bucket'],
      packages     = ['libbucket'],
      install_requires = """
configobj
commodity
requests
requests-futures
hgapi
gitapi""".split()
      )
