#!/usr/bin/env python
#
# Copyright (C) 2010 Martin Owens
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import os
import sys

sys.path.insert(1, 'lib/gtkme')

from distutils.core import setup
from version import __version__, __pkgname__

# remove MANIFEST. distutils doesn't properly update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

setup(
        name             = __pkgname__,
        version          = __version__,
        description      = 'Amazing interface for wrapping python-gtk applications and make programming fun again.',
        long_description = "Manages an Application with Gtk windows, forms, lists and other complex items easily.",
        url              = 'https://code.launchpad.net/~doctormo',
        author           = 'Martin Owens',
        author_email     = 'doctormo@gmail.com',
        platforms        = 'linux',
        license          = 'GPLv3',
        packages         = [ 'gtkme' ],
        package_dir      = {'': 'lib'}
    )

