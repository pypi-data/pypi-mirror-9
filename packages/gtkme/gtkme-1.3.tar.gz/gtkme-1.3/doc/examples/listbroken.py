#!/usr/bin/python
#
# Copyright 2012 Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#
"""
Sample example application using GtkMe
"""

import os
import sys
import logging

# Directories where gtkme can be found locally
sys.path.insert(1, '../../lib')
sys.path.insert(1, './lib')

# Import the gtkme TreeView and ViewColumn class with the normal classes.
from gtkme import Window, GtkApp, TreeView, ViewColumn, ViewSort


class AppWindow(Window):
    """We need to load the window the list is in"""
    name = 'listapp'

    def load_widgets(self):
        self.mylist = TreeView(self.widget('listapp'))


class ListApp(GtkApp):
    glade_dir = './'
    app_name = 'listapp'
    windows = [ AppWindow ]


if __name__ == '__main__':
    try:
        app = ListApp(start_loop=True)
    except KeyboardInterrupt:
        logging.info("User Interputed")
    logging.debug("Exiting Application")





