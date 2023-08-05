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
Wraps the gtk treeview and iconview in something a little nicer.
"""

import os
import mimetypes
import logging

from listview import TreeView, ViewColumn
from pixmap import ICON_THEME
from gi.repository import Gtk

MIME_CACHE = {}

class File(object):
    """Represent a file on the system"""
    def __init__(self, path, item=None):
        self.path = path
        self.item = item
        self.mime = mimetypes.guess_type(path)[0] or 'text/plain'
        if not hasattr(self, 'icon'):
            self.icon = self.get_icon()

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def parent(self):
        return os.path.dirname(self.path)

    def get_icon(self):
        """Returns the right gnome icon"""
        global MIME_CACHE
        if not MIME_CACHE.has_key(self.mime):
            for possible in ( self.mime,
                              self.mime.replace('/', '-'),
                              self.mime.replace('/', '-x-'),
                              'text-plain',
                            ):
                if ICON_THEME.has_icon(possible):
                    MIME_CACHE[self.mime] = possible
                    break
        return MIME_CACHE[self.mime]

    def isfile(self):
        return True

    def ishidden(self):
        return self.name[0] == '.'

    def __unicode__(self):
        return self.path

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return "<%s '%s'>" % (type(self).__name__, self.path)


class Directory(File):
    """Represent a dir on the system"""
    @property
    def icon(self):
        return 'gtk-directory'

    def isfile(self):
        return False

class FileTreeView(TreeView):
    """Load a treeview as a look at directories"""
    sorting = Gtk.SortType.ASCENDING
    file_class = File
    dir_class = Directory
    column_name = 'File Listing'
    column_size = 16

    def __init__(self, *args, **kwargs):
        self.show_all = kwargs.pop('show_all', False)
        kwargs['text'] = 'name'
        TreeView.__init__(self, *args, **kwargs)
        self.path = None

    def change_directory(self, path):
        """Change the current directory"""
        if not os.path.exists(path):
            raise IOError("Can't view path '%s' doesn't exist." % path)
        self.path = path
        self.update()

    def walk(self):
        """Over-ride this method if you want to construct file trees"""
        return os.walk(self.path, topdown=True)

    def clear(self):
        """Clear and disable"""
        TreeView.clear(self)
        self.set_sensitive(False)

    def filter(self, item):
        """Filter an item (over-ride to make use)"""
        return True

    def update(self):
        """Refresh the contents of the tree view"""
        self.clear()
        parents = {}
        for root, dirs, files in self.walk():
            if root == self.path or root == '':
                parent = None
            elif parents.has_key(root) and parents[root]:
                parent = parents[root]
            else:
                print "Skipping %s: %s" % (root, parents.keys())
                # parent skipped, so child skipped too
                continue

            for name in dirs:
                path = os.path.join(root, name)
                parents[path] = self.add_item(self.dir_class(path, self), parent)

            for name in files:
                self.add_item(self.file_class(os.path.join(root, name), self), parent)

        self.set_sensitive(True)


    def add_item(self, item, parent=None):
        if (not item.ishidden() or self.show_all) and self.filter(item):
            return TreeView.add_item(self, item, parent)

