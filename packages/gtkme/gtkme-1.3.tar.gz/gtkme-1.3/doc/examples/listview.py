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
from gtkme import Window, GtkApp, TreeView, ViewColumn, ViewSort, Separator


class ExampleTreeView(TreeView):
    """Show how easy it is to make a list of items with icons."""
    def get_markup(self, item):
        return item._foo

    def setup(self, widget):
        """Setup the treeview with one or many columns manually"""
        # Data for text is pulled out of the string of the object (i.e. __unicode__)
        # If no icon is specified then no icon will apear. Default is off.
        self.ViewColumn('Column Name')

        # Option two, specify the attribute names to pull from using strings.
        # A tuple means the second value will be used as a default if no value.
        # market template and icon options can be added to tweak the display.
        self.ViewColumn('Second Column', expand=True,
            text='second', template="<b>%s</b>",
            icon=('icon', 'default-icon'), pad=0, size=12 )

        # Option three is completely manual, specifying a method to call to
        # Get the item's data, item is suplied as the only argument.
        self.ViewColumn('Third Column', expand=False,
            text=self.get_markup, template="<i>%s</i>",
            icon=lambda item: item.icon, pad=6, size=22)

        # Sort can sort by comparing column values, or give priority to terms.
        self.ViewSort(data=self.get_markup, ascending=True, contains='third')


class Item(object):
    """All List Items are Objects"""
    def __init__(self, name, second, icon):
        self._foo = name
        self.second = second
        self.icon = icon

    def __unicode__(self):
        return self._foo


class AppWindow(Window):
    """We need to load the window the list is in"""
    name = 'listapp'

    def load_widgets(self):
        self.a = self.load_listwidget(TreeView, 'automatic')
        self.b = self.load_listwidget(ExampleTreeView, 'manual')

    def load_listwidget(self, container, name):
        result = container(self.widget(name), selected=self.signal)

        # Add items one at a time
        result.add_item(Item('First Item', '1', 'gtk-quit'))

        # Add using an iterator many items
        result.add([
            Item('Second Item', '4', 'gtk-close'),
            Item('Third Item', '12', 'gtk-open'),
            Item('Fouth Item', '101011', 'find'),
        ])
        return result
    
    def signal(self, item):
        print "Item passed '%s' vs Item selected '%s'" % (unicode(item), unicode(self.a.selected))



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





