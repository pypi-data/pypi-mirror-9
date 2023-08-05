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
Example using an icon view instead of a list view.
"""

import os
import sys
import logging

# Directories where gtkme can be found locally
sys.path.insert(1, '../../lib')
sys.path.insert(1, './lib')

# Import the gtkme TreeView and ViewColumn class with the normal classes.
from gtkme import Window, GtkApp, IconView


class Item(object):
    """Example item to populate the icons with"""
    def __init__(self, string, icon):
        self.string = string
        self.icon = icon


class ExampleIconView(IconView):
    """Show how easy it is to make a bunch of icons."""
    def get_markup(self, item):
        return item.string

    def get_icon(self, item):
        return item.icon


class IconViewWindow(Window):
    """We need to load the window the list is in"""
    name = 'iconviewapp'

    def load_widgets(self):
        self.mylist = ExampleIconView(self.widget('iconview'), selected=self.signal)
        self.mylist.add_item(Item('First Item', 'gtk-quit'))

        self.mylist.add([
            Item('Second Item', 'gtk-close'),
            Item('Third Item', 'gtk-open'),
            Item('Fouth Item', 'find'),
        ])
    
    def signal(self, item):
        print "Item selected! %s" % item.string



class IconViewApp(GtkApp):
    glade_dir = './'
    app_name = 'iconviewapp'
    windows = [ IconViewWindow ]


if __name__ == '__main__':
    try:
        app = IconViewApp(start_loop=True)
    except KeyboardInterrupt:
        logging.info("User Interputed")
    logging.debug("Exiting Application")





