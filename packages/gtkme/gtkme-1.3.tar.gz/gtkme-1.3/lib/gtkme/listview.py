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

import logging
from gi.repository import Gtk, Gdk, GObject, GdkPixbuf, Pango

from pixmap import PixmapManager, SizeFilter

def default(item, attr, d=None):
    """Python logic to choose an attribute, call it if required and return"""
    if hasattr(item, attr):
        prop = getattr(item, attr)
        if callable(prop):
            prop = prop()
        return prop
    #logging.warning("No property '%s.%s'" % (type(item).__name__, attr))
    return d

def item_property(name, d=None):
    def inside(item):
        return default(item, name, d)
    return inside

def label(obj):
    if isinstance(obj, tuple):
        return ' or '.join([ label(o) for o in obj ])
    if not isinstance(obj, type):
        obj = type(obj)
    if hasattr(obj, '__name__'):
        return obj.__name__
    return unicode(obj)

class BaseView(object):
    """Controls for tree and icon views, a base class"""
    widget_type = None

    def __init__(self, widget, selected=None, unselected=None, liststore=None, **kwargs):
        if not isinstance(widget, self.widget_type):
            raise TypeError("Wrong widget type: Expected %s got %s" % ( label(self.widget_type), label(widget) ))
        if liststore != None and not isinstance(liststore, Gtk.ListStore):
            raise TypeError("Wrong widget type: Expected ListStore got %s" % label(liststore) )
        self.selected_signal = selected
        self.unselected_signal = unselected
        self._iids    = []
        self._list    = widget
        self.args     = kwargs
        self.selected = None
        self._model   = liststore
        self._data    = None
        self.no_dupes = True
        self.connect_signals()
        self.setup(self.remodel())
        super(BaseView, self).__init__()

    def connect_signals(self):
        """Try and connect signals to and from the view control"""
        signal = 'changed' # ComboBox
        if isinstance(self._list, Gtk.TreeView):
            signal = 'cursor_changed'
        elif isinstance(self._list, Gtk.IconView):
            signal = 'selection-changed'
        self._list.connect(signal, self.item_selected_signal)

    def remodel(self):
        """Setup the model and list"""
        return self._list

    def setup(self, slist):
        """Setup columns, views, sorting etc"""
        pass

    def add(self, target, parent=None):
        """Add all items from the target to the treeview"""
        for item in target:
            self.add_item(item, parent=parent)

    def add_item(self, item, parent=None):
        """Add a single item image to the control"""
        if item != None:
            iid = self.get_item_id(item)
            if iid:
                if iid in self._iids and self.no_dupes:
                    logging.debug("Ignoring item %s in list, duplicate." % iid)
                    return None
                self._iids.append(iid)
            return self._add_item(item, parent)
        else:
            raise Exception("Item can not be None.")

    def get_item_id(self, target):
        """Return if possible an id for this item,
           if set forces list to ignore duplicates,
           if returns None, any items added."""
        return target and None

    def replace(self, new_item, item_iter=None):
        """Replace all items, or a single item with object"""
        if item_iter:
            self.remove_item(target_iter=item_iter)
            self.add_item(new_item)
        else:
            self.clear()
            self._data = new_item
            self.add(new_item)

    def item_selected(self, item=None):
        """Base method result, called as an item is selected"""
        if self.selected != item:
            self.selected = item
            if self.selected_signal and item:
                self.selected_signal(item)
            elif self.unselected_signal and not item:
                self.unselected_signal(item)

    def remove_item(self, item=None, target_iter=None):
        """Remove an item from this view"""
        if target_iter and not item:
            return self._model.remove(target_iter)
        target_iter = self._model.get_iter_first()
        for itemc in self._model:
            if itemc[0] == item:
                return self._model.remove(target_iter)
            target_iter = self._model.iter_next(target_iter)

    def set_sensitive(self, s):
        """Proxy the GTK property for sensitivity"""
        self._list.set_sensitive(s)

    def clear(self):
        """Clear all items from this treeview"""
        self._iids = []
        self._model.clear()

    def item_double_clicked(self, items):
        """What happens when you double click an item"""
        return items # Nothing

    def get_item(self, item_iter):
        """Return the object of attention from an iter"""
        if isinstance(item_iter, Gtk.TreePath):
            item_iter = self._model.get_iter(item_iter)
        return self._model[item_iter][0]

    def get_row(self, item):
        """Returns the iter for this item"""
        for i in self._model:
            if i[0] == item:
                return i
        return None

    def set_selected(self, item):
        """Sets the selected item to this item"""
        row = self.get_row(item)
        if row:
            self._list.set_cursor(row.path)


class TreeView(BaseView):
    """Controls and operates a tree view."""
    column_size = 16
    widget_type = (Gtk.TreeView, Gtk.ComboBox)

    def selected_items(self, treeview=None):
        """Return a list of selected item objects"""
        item_iter = None
        if not treeview:
            treeview = self._list
        # This may need more thought, only returns one item
        if isinstance(treeview, Gtk.TreeView):
            select = treeview.get_selection()
            if select:
                return [ self.safe_get_item(row) for row in select.get_selected_rows()[1] ]
        else:
            return [ self.safe_get_item( treeview.get_active_iter() ) ]

    def safe_get_item(self, item_iter):
        try:
            if item_iter != None:
                return self.get_item(item_iter)
        except TypeError, msg:
            logging.error("Error %s" % msg)
        logging.warn("No items selected for list?")
        return None

    def _add_item(self, item, parent):
        return self._model.append(parent, [item])

    def item_selected_signal(self, treeview):
        """Signal for selecting an item"""
        items = self.selected_items(treeview)
        if items:
            return self.item_selected( items[0] )

    def item_button_clicked(self, treeview, event):
        """Signal for mouse button click"""
        if event.type == Gdk.EventType.BUTTON_PRESS:
            self.item_double_clicked( self.selected_items(treeview)[0] )

    def expand_item(self, item):
        """Expand one of our nodes"""
        self._list.expand_row(self._model.get_path(item), True)

    def remodel(self):
        """Set up an icon view for showing gallery images"""
        if not self._model:
            self._model = Gtk.TreeStore(GObject.TYPE_PYOBJECT)
        self._list.set_model(self._model)
        return self._list

    def setup(self, svlist):
        """Creates a default single column, override if this isn't what you want"""
        sort_by = self.args.pop('sort', self.args.get('text', unicode))
        self.sort = self.ViewSort(sort_by, self.args.pop('ascending', False))

        kwargs = { 'name': '', 'expand': True, 'size': self.column_size }
        kwargs.update( self.args )
        self.ViewColumn( **kwargs )

    def ViewColumn(self, *args, **kwargs):
        return ViewColumn(self._list, *args, **kwargs)

    def ViewSort(self, *args, **kwargs):
        return ViewSort(self._list, *args, **kwargs)


class IconView(BaseView):
    """Allows a simpler IconView for DBus List Objects"""
    pixmaps = PixmapManager('', pixmap_dir='./', size=32)
    widget_type = Gtk.IconView

    def remodel(self):
        """Setup the icon view control and model"""
        self._model = Gtk.ListStore(GObject.TYPE_PYOBJECT, str, GdkPixbuf.Pixbuf)
        self._list.set_model(self._model)
        return self._list

    def setup(self, svlist):
        """Setup the columns for the iconview"""
        svlist.set_markup_column(1)
        svlist.set_pixbuf_column(2)

    def get_markup(self, item):
        """Default text return for markup."""
        return default(item, 'name', str(item))

    def get_icon(self, item):
        """Default icon return, pixbuf or gnome theme name"""
        return default(item, 'icon', None)

    def _get_icon(self, item):
        return self.pixmaps.get(self.get_icon(item))

    def _add_item(self, item, parent):
        # Each item's properties must be stuffed into the
        # ListStore directly or the stupid IconView won't
        # see them.
        return self._model.append([item,
            self.get_markup(item),
            self._get_icon(item)])

    def item_selected_signal(self, icon_view):
        """Item has been selected"""
        return icon_view.get_selected_items()


class ViewSort(object):
    """Refute the use of sorting in gnome, bleh!"""
    def __init__(self, widget, data=None, ascending=False, exact=None, contains=None):
        self.tree = None
        self.data = data
        self.asc  = ascending
        self.comp = exact and exact.lower() or None
        self.cont = contains
        self.tree = widget
        self.resort()

    def sort_func(self, model, iter1, iter2, data):
        value1 = self.data(model.get_value(iter1, 0))
        value2 = self.data(model.get_value(iter2, 0))
        if value1 == None or value2 == None:
            return 0
        if self.comp:
            if cmp(self.comp, value1.lower()) == 0:
                return -1
            elif cmp(self.comp, value2.lower()) == 0:
                return 1
            return 0
        elif self.cont:
           if self.cont in value1.lower():
               return -1
           elif self.cont in value2.lower():
               return 1
           return 0 
        if value1 < value2:
            return 1
        if value2 < value1:
            return -1
        return 0

    def resort(self):
        model = self.tree.get_model()
        model.set_sort_func(0, self.sort_func, None)
        if self.asc:
            model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        else:
            model.set_sort_column_id(0, Gtk.SortType.DESCENDING)


class ViewColumn(object):
    """Add a column to a gtk treeview without dealing with gnomes"""
    def __init__(self, widget, name, expand=False, text=unicode, wrap=None, template=None,
        icon=False, pad=0, size=None, pixmaps=None, renderer=None):

        # Manager where icons will be pulled from
        self.pixmaps = pixmaps or PixmapManager('', pixmap_dir='./', size=size)
        self.size = SizeFilter(self.pixmaps, size=size)

        if isinstance(widget, Gtk.TreeView):
            column = Gtk.TreeViewColumn((name))
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            column.set_expand(expand)
            widget.append_column(column)
        else:
            # Deal with possible drop down lists
            column = widget

        # Separators should do something
        widget.set_row_separator_func(self.is_separator, None)

        if renderer != None:
            renderer_custom = renderer()
            column.pack_start(renderer_custom, False)
            column.set_cell_data_func(renderer_custom,
                self.data_func(), None)

        # The icon
        if icon != False:
            renderer_icon = Gtk.CellRendererPixbuf()
            if pad:
                renderer_icon.set_property("ypad", pad)
                renderer_icon.set_property("xpad", pad)
            column.pack_start(renderer_icon, False)
            if not icon or icon == True:
                icon = self.default_icon
            column.set_cell_data_func(renderer_icon,
                self.icon_func(icon), None)

        if renderer == None:
            # The name
            renderer = Gtk.CellRendererText()
            if wrap:
                renderer.props.wrap_width = wrap
                renderer.props.wrap_mode = Pango.WrapMode.WORD

            column.pack_start(renderer, True)
            if not text:
                text = self.default_text

            renderer.props.background_set = True
            renderer.props.foreground_set = True

            column.set_cell_data_func(renderer,
                self.text_func(text, template), None)

        self._column = column

    def is_separator(self, model, item_iter, data):
        item = model.get_value(item_iter, 0)
        return isinstance(item, Separator)

    def clean(self, text, markup=False):
        """Clean text of any pango markup confusing chars"""
        if text == None:
            text = ''
        if isinstance(text, (basestring, int, float)):
            if markup:
                text = unicode(text).replace('<', '&lt;').replace('>', '&gt;')
            return unicode(text).replace('&', '&amp;')
        elif isinstance(text, dict):
            target = {}
            for key in text.keys():
                target[key] = self.clean(text[key])
            return target
        elif isinstance(text, list) or isinstance(text, tuple):
            target = []
            for value in text:
                target.append(self.clean(value))
            return tuple(target)
        else:
            raise TypeError("Unknown value type for text: %s" % str(type(text)))

    def get_callout(self, call, default=None):
        """Returns the right kind of method"""
        if isinstance(call, tuple):
            (call, default) = call
        if isinstance(call, basestring):
            call = item_property(call, default)
        return call

    def data_func(self):
        """Wrap a non-text data function"""
        def internal(column, cell, model, item_iter, data):
            item = model.get_value(item_iter, 0)
            cell.set_property("data", item)
        return internal

    def text_func(self, call, template=None):
        """Wrap up our text functionality"""
        callout = self.get_callout(call)
        def internal(column, cell, model, item_iter, data):
            if self.is_separator(model, item_iter, data):
                return
            item = model.get_value(item_iter, 0)
            text = callout(item)
            if template:
                text = template % self.clean(text, markup=True)
            else:
                text = self.clean(text)
            cell.set_property("markup", unicode(text))
            self._set_background(cell, item)
        return internal

    def icon_func(self, call):
        """Wrap, wrap wrap the func"""
        callout = self.get_callout(call)
        def internal(column, cell, model, item_iter, data):
            if self.is_separator(model, item_iter, data):
                return
            item = model.get_value(item_iter, 0)
            icon = callout(item)
            if (icon and isinstance(icon, basestring) and self.pixmaps) or icon == None:
                # Expect a Gnome theme icon
                icon = self.pixmaps.get(icon)
            elif icon:
                icon = self.size.filter(icon)
            if icon:
                cell.set_property("pixbuf", icon)
                cell.set_property("visible", True)
                self._set_background(cell, item)
            else:
                cell.set_property("visible", False)
        return internal

    def _set_background(self, cell, item):
        """Internal method for setting the background color"""
        color = self.set_background(item)
        if color:
            cell.set_property("cell-background", color)

    def set_background(self, item):
        """Returns None, over-ride and return color string i.e. '#ff0000'"""
        return None

    def default_text(self, item):
        """Default text return for markup."""
        return default(item, 'name', str(item))

    def default_icon(self, item):
        """Default icon return, pixbuf or gnome theme name"""
        return default(item, 'icon', None)


class Separator(object):
    """Reprisentation of a separator in a list"""
    pass
