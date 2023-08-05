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
Interesting example using non-windows, lib-indicators with either
version of the standard from GIR will work.
"""

import os
import sys
import logging

# Directories where gtkme can be found locally
sys.path.insert(1, '../../lib')
sys.path.insert(1, './lib')

# Import the gtkme window and app class
from gtkme import GtkApp

from gtkme.indicator import Indicator


class AppIndicator(Indicator):
    """Indicators follow similar rules to windows, they're components
    of the application that are always loaded like primary windows.
    Exiting the indicator will not exit the application unless it's the
    only 'window' running."""

    desc = 'Indicator Example'
    icon = "gtk-close"
    active_desc = "Example while activated"
    active_icon = "gtk-open"

    def load_widgets(self):
        # New items are added with their text and connected signal
        self.new_item("Alert Me!", self.signal)
        self.new_item("Passive Me!", self.signal2)
        # Seperators are created like so
        self.new_separator()
        # The exit signal is already expected and built in.
        self.new_item("Exit", self.exit)
        print "Indicator Ready!"

    def signal(self, widget=None):
        self.activate(True)

    def signal2(self, widget=None):
        self.deactivate()



class SimpleApp(GtkApp):
    """The application can also load indicators when required."""
    windows = [ AppIndicator ]


if __name__ == '__main__':
    try:
        app = SimpleApp(start_loop=True)
    except KeyboardInterrupt:
        logging.info("User Interputed")
    logging.debug("Exiting Application")





