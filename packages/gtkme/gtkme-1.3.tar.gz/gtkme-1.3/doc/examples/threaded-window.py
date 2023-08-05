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
Threaded windows allow your application to do tasks involving heavy
computaion or downloading which will interface with the gui at
intersections, but for which you need the interface to remain responsive.
"""

import os
import sys
import logging
import time

# Directories where gtkme can be found locally
sys.path.insert(1, '../../lib')
sys.path.insert(1, './lib')

# Import the threaded window class like others
from gtkme import ThreadedWindow, GtkApp


class AppWindow(ThreadedWindow):
    """Just like any other window, except with threads."""
    # Use the existing app
    name = 'simpleapp'

    def sample_signal(self, widget=None):
        self.start_thread(self.thread_contents, "data")
        print "Thread Started! (see, not locked)"

    def thread_contents(self, data):
        timer = 0
        # This is where the action happens.
        while timer < 100:
            time.sleep(1)
            print "Ping"
            timer += 1
            # You can't use Gtk widgets here without making
            # a mess of the python GIL, so... call out to...
            self.call('out_of_thread', "Foo %d" % timer)
            # Sometimes it's possible to see if the window has
            # closed and kill the internal loop or break it.
            if self._closed:
                break

    def out_of_thread(self, foo):
        # But here outside of the thread, we can modify Gtk
        self.widget("button1").set_label(foo)


class ThreadedWindowApp(GtkApp):
    """This Application loads threaded windows just like any other."""
    glade_dir = './'
    app_name = 'threadedwindowapp'
    windows = [ AppWindow ]


if __name__ == '__main__':
    try:
        app = ThreadedWindowApp(start_loop=True)
    except KeyboardInterrupt:
        logging.info("User Interputed")
    logging.debug("Exiting Application")





