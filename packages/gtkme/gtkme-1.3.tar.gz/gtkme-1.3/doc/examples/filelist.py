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
Use of the file listing functionality in a tree view.

The tree view is more of an extended example of how to use the tree view
models, but is also useful for anyone who wants to display lists of files.
"""

import os
import sys
import logging

# Directories where gtkme can be found locally
sys.path.insert(1, '../../lib')
sys.path.insert(1, './lib')

from gtkme import Window, GtkApp

# Import the file view
from gtkme.listfiles import FileTreeView


class ListFilesWindow(Window):
    """Show files in our list view, we can reuse the listapp glade file too."""
    name = 'listapp'

    def load_widgets(self):
        self.myfiles = FileTreeView(self.widget('manual'), selected=self.signal)
        self.myfiles.change_directory('/var/log/')
    
    def signal(self, item):
        print "Item selected! %s" % unicode(item)



class ListApp(GtkApp):
    glade_dir = './'
    app_name = 'listfilesapp'
    windows = [ ListFilesWindow ]


if __name__ == '__main__':
    try:
        app = ListApp(start_loop=True)
    except KeyboardInterrupt:
        logging.info("User Interputed")
    logging.debug("Exiting Application")





