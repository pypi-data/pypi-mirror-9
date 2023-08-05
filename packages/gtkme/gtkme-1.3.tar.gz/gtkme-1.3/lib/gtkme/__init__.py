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
GtkMe is a wrapper layer to make interacting with Gtk a little less painful.
The main issues with Gtk is that it expects an aweful lot of the developer,
code which is repeated over and over and patterns which every single developer
will use are not given easy to use convience functions.

This makes Gtk programming dry, unattractive and error prone. GtkMe steps in
between and adds in all those missing bits. It's not meant to replace Gtk and
certainly it's very possible to remove GtkMe completely and fall back on Gtk
and threading only. But better you than me fine sir.
"""

import threading
import os
import logging

from window import Window, ChildWindow, ThreadedWindow
from forms import FormWindow
from listview import TreeView, IconView, ViewColumn, ViewSort, Separator
from pixmap import PixmapManager, AnimationManager
from main import app, Thread, GtkApp, FakeWidget
from indicator import Indicator
from version import __version__

