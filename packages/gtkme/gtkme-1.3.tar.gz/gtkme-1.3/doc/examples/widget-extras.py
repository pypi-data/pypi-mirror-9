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
Using the widgets in a window to do interesting things.
"""

import os
import sys
import logging

# Directories where gtkme can be found locally
sys.path.insert(1, '../../lib')
sys.path.insert(1, './lib')

# Import the gtkme TreeView and ViewColumn class with the normal classes.
from gtkme import Window, GtkApp, PixmapManager
from listview import AppWindow as ListViewWindow


class HoldingWindow(Window):
    """A window to hold other widgets."""
    name = 'widgetextra'

    def load_widgets(self):
        target = self.widget('target')
        # Cloning is a way of allowing your designers to control all
        # the properties of elements which may need to be duplicated
        # Within the code.
        for x in range(2):
            widget = self.clone_widget('dupe', True)
            target.pack_start(widget, True, True, 0)
        # Adding a window as an element allows reuse of code and modualisation
        # of the design, can be useful for certain tab based applications.
        widget = self.load_window_extract('listapp')
        target.pack_start(widget, True, True, 5)
        widget.show_all()



class ListApp(GtkApp):
    glade_dir = './'
    app_name = 'extrawidgets'
    windows = [ HoldingWindow, ListViewWindow ]


if __name__ == '__main__':
    try:
        app = ListApp(start_loop=True)
    except KeyboardInterrupt:
        logging.info("User Interputed")
    logging.debug("Exiting Application")





