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

# Import the gtkme window and app class
from gtkme import Window, GtkApp


class AppWindow(Window):
    """Each window has its own class, you can load multiple windows
    of the same type. This is a Primary window which means it is
    automatically shown when the app loads."""

    # Name of the window, this is both the filename of the glade
    # file 'simpleapp.glade' or 'simpleapp.ui' and also the id of
    # the window inside the glade file.
    name = 'simpleapp'

    # All signals are pre-bound, so you don't have to do anything
    # Except create the right definition in your python class.
    def sample_signal(self, widget=None):
        print "Button pressed!"

    # Exit/destroy signals are taken care of automatically.


class SimpleApp(GtkApp):
    """The application is in charge of loading the glade files, loads
    the windows"""
    # Where will the app load glade files from? This can be brought in
    # from a setup or configuration file for multiple platform deplyments.
    glade_dir = './'
    # Name of the application for logging.
    app_name = 'simpleapp'
    # A list of windows, windows that are primary windows will load
    # with the app, ChildWindows will load when requested using
    # app.load_window('window_name')
    windows = [ AppWindow ]


if __name__ == '__main__':
    # The App class will manage your gtk loop for you
    # Making sure to destroy it on exiting the last window.
    try:
        app = SimpleApp(start_loop=True)
    except KeyboardInterrupt:
        logging.info("User Interputed")
    logging.debug("Exiting Application")





