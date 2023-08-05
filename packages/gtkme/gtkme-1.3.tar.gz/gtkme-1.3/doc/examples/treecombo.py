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
Example showing trees of items in a list, seperators and comboboxes.
"""

import os
import sys
import logging

# Directories where gtkme can be found locally
sys.path.insert(1, '../../lib')
sys.path.insert(1, './lib')

# Import the gtkme TreeView and ViewColumn class with the normal classes.
from gtkme import Window, GtkApp, TreeView, ViewColumn, Separator


class Item(object):
    """Example item to populate the list with"""
    def __init__(self, string, icon):
        self.string = string
        self.icon = icon


class ExampleTreeView(TreeView):
    """Show how easy it is to make a list of items with icons."""
    def get_markup(self, item):
        return item.string

    def get_icon(self, item):
        return item.icon

    def get_second(self, item):
        return item.second

    def setup(self, svlist):
        """Setup the treeview with one or many columns"""
        column = ViewColumn(svlist, 'Column Name', expand=True,
            text=self.get_markup, template="<b>%s</b>",
            icon=self.get_icon, pad=6, size=22 )



class AppWindow(Window):
    """We need to load the window the list is in"""
    name = 'treecombo'

    def load_widgets(self):
        # The same tree view can be used for both lists, trees and combo boxes
        self.mytree = ExampleTreeView(self.widget('treeview'), selected=self.signal)
        self.mydrop = ExampleTreeView(self.widget('combobox'), selected=self.signal)

        parent = self.mytree.add_item(Item('First Item', 'gtk-quit'))
        self.mytree.add_item(Item('Second Item', 'gtk-close'), parent)
        self.mytree.add_item(Separator())
        self.mytree.add_item(Item('Seperated Item', 'gtk-paste'))

        self.mydrop.add([
            Item('Third Item', 'gtk-open'),
            Separator(),
            Item('Fouth Item', 'find'),
            Item('Fith Item', 'gtk-cut'),
        ])
    
    def signal(self, item):
        print "Item selected! %s" % item.string



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





