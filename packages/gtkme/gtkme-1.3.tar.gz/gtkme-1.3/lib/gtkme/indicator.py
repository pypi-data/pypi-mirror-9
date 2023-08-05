#
# Copyright 2011 Martin Owens <doctormo@gmail.com>
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
Creates some nice functions for indicators
"""

import os
import logging
from gi.repository import Gtk

try:
    from gi.repository.AppIndicator3 import (
        IndicatorStatus as Status, IndicatorCategory as Category,
        Indicator as RawIndicator
    )
    APPLICATION_STATUS = Category.APPLICATION_STATUS
except ImportError:
    try:
        from gi.repository.AppIndicator import Status, Category
        from gi.repository.AppIndicator import AppIndicator as RawIndicator
        APPLICATION_STATUS = Category.APPLICATIONSTATUS
    except ImportError:
        APPLICATION_STATUS = None
        logging.debug("Indicator is disabled, AppIndicator GIR missing.")


class Indicator(object):
    """Provides an inheritable indicator service, we would have
    inherited directly from RawIndicator, but GObject forbids it."""
    category = APPLICATION_STATUS
    desc = 'New Indicator'
    icon = 'gtk-edit'
    active_desc = 'Active New Indicator'
    active_icon = 'gtk-attention'
    primary = True
    name = 'indicator'

    def __init__(self, gapp, parent=None, debug=False, callback=None):
        self.gapp = gapp
        icon = debug and 'gtk-edit' or self.icon
        active_icon = debug and 'gtk-save' or self.active_icon
        self.raw = RawIndicator.new(self.desc, icon, self.category)
        self.raw.set_status(Status.ACTIVE)
        self.raw.set_attention_icon_full(active_icon, self.active_desc)
        # create a menu
        self.menu = Gtk.Menu()
        self.raw.set_menu(self.menu)
        self.wid = self.desc

    def init(self, *args, **kwargs):
        """Load widgets (do not override)"""
        self.load_widgets()

    def load_widgets(self):
        """Override this method to load your menus"""
        pass

    def new_menu(self, message, parent=None):
        """Create a new parent menuitem and attach a new menu to it"""
        if not parent:
            parent = self.menu
        item = self.new_subitem(message, parent, None)
        menu = Gtk.Menu()
        item.set_submenu(menu)
        return (item, menu)

    def new_item(self, message, method, *args):
        """Create a new menuitem and attach it to the indicator menu"""
        return self.new_subitem(message, self.menu, method, *args)

    def new_subitem(self, message, parent, method, *args):
        """Create a new menuitem, specify the parent menu object"""
        item = Gtk.MenuItem(message)
        item.show()
        parent.append(item)
        if method:
            item.connect("activate", method, *args)
        return item

    def new_separator(self, parent=None):
        """Starts a new section by creating a seperator"""
        if not parent:
            parent = self.menu
        item = Gtk.SeparatorMenuItem()
        item.show()
        parent.append(item)
        return item

    def deactivate(self):
        """Set indicator to passive"""
        self.raw.set_status(Status.PASSIVE)

    def activate(self, alert=False):
        """Set indicator to active"""
        if alert:
            self.raw.set_status(Status.ATTENTION)
        else:
            self.raw.set_status(Status.ACTIVE)

    def exit(self, widget=None):
        """Exit the indicator, destroy it"""
        self.gapp.remove_window(self)

