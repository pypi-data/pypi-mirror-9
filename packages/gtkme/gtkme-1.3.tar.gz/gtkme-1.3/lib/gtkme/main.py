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
Base Classes etc.
"""

import threading
import os
import logging
import signal
from gi.repository import Gtk, GLib, GObject

class Thread(threading.Thread):
    """Special thread object for catching errors and logging them"""
    def run(self, *args, **kwargs):
        """The code to run when the thread us being run"""
        try:
            super(Thread, self).run(*args, **kwargs)
        except Exception, message: #W:0041
            logging.exception(message)


class LoopDe(object):
    """Base class for the looping interface"""
    def start(self):
        raise NotImplementedError("Loop interface needs a start() method.")

    def loop(self):
        raise NotImplementedError("Loop interface needs a loop() method.")

    def stop(self):
        raise NotImplementedError("Loop interface needs a stop() method.")

class Options(dict):
    """Simple dictionary of options and alternative static attribute defaults"""
    def __init__(self, dictionary, obj):
        self.obj = obj
        self.update(dictionary)

    def __getitem__(self, name):
        if self.has_key(name):
            return dict.get(self, name)
        if hasattr(self.obj, name):
            return getattr(self.obj, name)
        raise KeyError("Can't find option: %s" % name)

    def __getattr__(self, name):
        return self[name]


class GtkApp(object):
    """
    This wraps gtk builder and allows for some extra functionality with
    windows, especially the management of gtk main loops.

    Class Options

    app_name:   Name of application, for logging and translations.
    glade_dir:  Folder containing all glade files.
    prefix:     Folder prefix added to glade_dir.
    windows:    List of window classes attached to this App.

    Object Attributes:

    start_loop - If set to true will start a new gtk main loop.
    **kwargs   - Passed to primary window when loaded.
    """
    prefix  = ''
    windows = None

    @property
    def glade_dir(self):
        """This is often the local directory"""
        return './'

    @property
    def app_name(self):
        """Set this variable in your class"""
        raise NotImplementedError("You need to set 'app_name' in the class.")

    def __init__(self, **kwargs):
        self._loaded   = {}
        self._inital   = {}
        self._primary  = None
        self.main_loop = GLib.main_depth()
        self.opt       = Options(kwargs, self)
        # Now start dishing out initalisation
        self.init_gui()
        # Start up a gtk main loop when requested
        if self.opt.start_loop:
            logging.debug("Starting new GTK Main Loop.")
            # Add a signal to force quit on Ctrl+C (just like the old days)
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            Gtk.main()

    def ui_file(self, window):
        """Load any given gtk builder file from a standard location."""
        # Explaining Rant: I dislike Gnome developers, for some reason they
        # think it's funny to muddle the concepts of application and window to
        # such a degree that it's impossible to create windows as seperated
        # classes handeling their own events. This happens because they have
        # stuffed a multi-window ui file into a single window ui idea, I can
        # only deduce that Gnome/Gtk developers have no concept of gobject
        # programming and are in reality an infinity of chimps typing on banna
        # phones, may entropy have mercy on their souls.
        path = os.path.join(self.glade_dir, self.opt.prefix, "%s.glade" % window)
        if not os.path.exists(path):
            path = os.path.join(self.glade_dir, self.opt.prefix, "%s.ui" % window)
            if not os.path.exists(path):
                raise Exception("Gtk Builder file is missing: %s" % path)
        return path

    def init_gui(self):
        """Initalise all of our windows and load their signals"""
        if self.opt.windows:
            for cls in self.opt.windows:
                window = cls
                logging.debug("Adding window %s to GtkApp\n" % window.name )
                self._inital[window.name] = window
            for window in self._inital.values():
                if window.primary:
                    if not self._primary:
                        self._primary = self.load_window(window.name)
                    else:
                        logging.debug("More than one window is set Primary!")
        if not self.opt.windows or not self._primary:
            logging.warn("No primary window found for '%s' app." % self.app_name)

    def load_window(self, name, *args, **kwargs):
        """Load a specific window from our group of windows"""
        window = self.proto_window(name)
        window.init(*args, **kwargs)
        return window

    def proto_window(self, name):
        """Loads a glade window as a window without initalisation, used for
        extracting widgets from windows without loading them as windows"""
        logging.debug("Loading '%s' from %s" % (name, str(self._inital)))
        if self._inital.has_key(name):
            # Create a new instance of this window
            window = self._inital[name](self)
            # Save the window object linked against the gtk window instance
            self._loaded[window.wid] = window
            return window
        raise KeyError("Can't load window '%s', class not found." % name)

    def remove_window(self, window):
        """Remove the window from the list and optional exit"""
        if self._loaded.has_key(window.wid):
            self._loaded.pop(window.wid)
        else:
            logging.warn("Tried unload window '%s' on exit, it's already gone."
                % window.name)
            logging.debug("Loaded windows: %s" % str(self._loaded))
        if not self._loaded:
            self.exit()

    def exit(self):
        """Exit our gtk application and kill gtk main if we have to"""
        if self.main_loop < GLib.main_depth():
            # Quit Gtk loop if we started one.
            logging.debug("Quit '%s' Main Loop." % (
                self._primary and self._primary.name or 'program'))
            Gtk.main_quit()
            # You have to return in order for the loop to exit
            return 0


class FakeWidget(object):
    """A fake widget class that can take calls"""
    def __init__(self, name):
        self._name = name

    def __getattr__(self, name):
        return self.fake_method

    def __bool__(self):
        return False

    def __nonzero__(self):
        return False

    def fake_method(self, *args, **kwargs):
        """Don't do anything, this is fake"""
        logging.info("Calling fake method: %s:%s" % (str(args), str(kwargs)))
        return None

    def information(self):
        """This is a dumb method too"""
        return None


class AutoApp(GtkApp):
    """Automatic application"""
    @property
    def glade_dir(self):
        return './'
    windows = [ ] #AppWindow ]


def app(*args, **kwargs):
    """An automatic application, loads the required everything"""
    kwargs['start_loop'] = True
    try:
        app = AutoApp(*args, **kwargs)
    except KeyboardInterrupt:
        logging.error("User Interputed")


