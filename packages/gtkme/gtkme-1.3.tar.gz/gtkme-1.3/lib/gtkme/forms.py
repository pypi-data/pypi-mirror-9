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
Special notebook based pages form child window for use with glade.
"""

import logging

from gi.repository import Gtk, Gdk, GLib, GObject

try:
    from validator import Validator
except ImportError:
    Validator = None

from window import ChildWindow


class FormWindow(ChildWindow):
    """
    Base class from windows which act as forms, they expect to contain all
    kinds of fields and be able to validate them and pass the data back to
    the callback when required.
    """
    fields = None

    def __init__(self, *args, **kwrds):
        self.done      = False
        self._data     = {}
        self._marked   = {}
        self._pindex   = []
        super(FormWindow, self).__init__(*args, **kwrds)
        self._notebook = self.if_widget('pages')
        if self._notebook:
            self._notebook.connect("switch-page", self.update_buttons)
            for n in range(self._notebook.get_n_pages()):
                page = self._notebook.get_nth_page(n)
                self._pindex.append(page)

    def pre_exit(self):
        """Callback on exit with form data as args."""
        if self.callback and self.done:
            self.callback(**self.data())
            # Reset callback so super doesn't execute it.
            self.callback = None

    def data(self):
        """Access the data in the window."""
        # Refresh the data when the window is still alive
        # But don't when the window is closed (because we can't)
        if not self.dead:
            self._data = self.get_data()
        return self._data

    def get_data(self):
        """Return the data from all fields on the window."""
        if self.fields:
            return self.all_field_data()
        logging.warn("Can't get data, you need to define fields or create get_data function.")
        return None

    def next_page(self, widget=None):
        """When we have pages calling this event will move to the next"""
        working = self.is_valid(self._notebook.get_current_page())
        if working != True:
            return self.mark_invalid(working)
        # Call apply on this form if we've reached the end.
        if self._notebook.get_n_pages()-1 == self._notebook.get_current_page():
            return self.apply(widget)
        else:
            self._notebook.next_page()
        return widget

    def previous_page(self, widget=None):
        """when we have pages call this event and go back to the prev page"""
        notebook = self.if_widget('pages')
        notebook.prev_page()
        return widget

    def this_page(self, overide=None):
        """Return the current page we're on"""
        if overide == None:
            return self._notebook.get_current_page()
        return int(overide)

    @property
    def first_page(self):
        """Return the first page index, normally 0"""
        return 0

    @property
    def last_page(self):
        """Return the last page index, normally count -1"""
        return self._notebook.get_n_pages() - 1

    def update_buttons(self, widget, page_from, page_to):
        """Updates the previous, next and apply buttons"""
        this_page = self.this_page(page_to)
        # Enable the back button if the page is != 0
        self.update_button('previous', this_page > self.first_page)
        # Hide the forward and show the apply if the page is last
        if self.if_widget('apply'):
            self.update_button('apply', this_page == self.last_page)
            self.update_button('next', this_page < self.last_page)
        else:
            # Sometimes we hide the next button in glade so loading
            # screens can take the entire space. But now we need them.
            self.update_button('next', True)
        return this_page

    def update_button(self, name, enable):
        """Show/hide and/or enable/disable the named button"""
        #self.if_widget(name).set_sensitive(enable)
        self.if_widget(name).set_visible(enable)

    def set_page(self, pageid):
        """Set the form to a specific page"""
        if isinstance(pageid, int):
            self._notebook.set_current_page(pageid)
        elif isinstance(pageid, basestring):
            element = self.if_widget(pageid)
            if element and element in self._pindex:
                return self.set_page(self._pindex.index(element))
            else:
                raise KeyError("Couldn't find page element '%s'" % pageid)
        else:
            raise KeyError("Page id isn't an index or an element id.")

    def apply(self, widget=None):
        """Apply any changes as required by callbacks"""
        problems = self.is_valid()
        # True for is_valid or a list of problems
        if not problems or problems == True:
            logging.debug("Applying changes")
            self.done = True
            # Make sure arguments are stored.
            if not isinstance(self.data(), dict):
                logging.warn("%s data isn't a dictionary." % self.name)
            # Now exit the main application.
            self.destroy()
        else:
            self.mark_invalid(problems)
        return widget

    def is_valid(self, page=-1):
        "Return true if all data is valid or an array of invalid widget names." 
        # If fields is defined than we expect to do field validation.
        if self.fields:
            if isinstance(self.fields, list):
                # Checking single page
                if page >= 0 and page < len(self.fields):
                    return self.are_fields_valid(self.fields[page])
                else: # Checking all pages
                    for p in range(0, len(self.fields)):
                        errors = self.are_fields_valid(self.fields[p])
                        if errors != True:
                            return errors
            else: # No pages exist
                return self.are_fields_valid(self.fields)
        return True

    def are_fields_valid(self, f_def):
        """Returns true if the hash of field definitions are all valid."""
        if not f_def:
            return True
        if not Validator:
            logging.warn("Can't validate data: python-validator not installed.")
            return True
        data = self.field_data(f_def)
        errors = None
        field_list = []
        # Translate to xsd style syntax by transposing
        # the name into the hash from the key.
        for name in f_def.keys():
            field = f_def[name]
            field['name'] = name
            field['type'] = field.get('type', 'string')
            field_list.append( field )
        validator = Validator( { 'root' : field_list } )
#        try:
        errors = validator.validate( data )
#        except Exception, error:
#            logging.warn("Couldn't validate page, skipping validation: %s" % error)
        # Collect the errors and report on what fields failed
        if errors:
            result = []
            for err in errors.keys():
                if errors[err]:
                    result.append(err)
            return result
        # Otherwise we pass!
        return True

    def all_field_data(self):
        """Returns all of the fields we know about"""
        result = {}
        if isinstance(self.fields, list):
            for fields in self.fields:
                result.update(self.field_data(fields))
        return result

    def field_data(self, fields):
        """Return a simple hash of all the fields"""
        if not fields:
            return {}
        result = {}
        for name, field in fields.iteritems():
            widget = self.widget('field_' + name)
            if isinstance(widget, Gtk.TextView):
                buf = widget.get_buffer()
                start, end = ( buf.get_start_iter(), buf.get_end_iter() )
                result[name] = buf.get_text( start, end, True )
            elif isinstance(widget, Gtk.Entry):
                try:
                    result[name] = widget.get_text()
                except AttributeError:
                    result[name] = ''
            elif isinstance(widget, Gtk.ComboBox):
                # To avoid translations messing up the validation, with the
                # enumeration validation, this returns the index if no enum
                # is available, but will return the string if it is. Glade
                # is expected to translate, so don't translate your enum.
                active = widget.get_active()
                if active >= 0 and field.has_key('enumeration'):
                    active = field['enumeration'][active]
                result[name] = active
            elif isinstance(widget, Gtk.RadioButton):
                group = widget.get_group()
                if group:
                    for radio in group:
                        if radio.get_active():
                            result[name] = radio.get_label()
            elif isinstance(widget, Gtk.CheckButton) \
              or isinstance(widget, Gtk.Switch):
                result[name] = widget.get_active()
            elif widget:
                logging.warn("I can't understand '%s' fields for '%s'." % (str(type(widget)), name))
            else:
                logging.warn("Couldn't find field %s!" % name)
        return result

    def mark_invalid(self, invalids):
        """This is what happens when we're not valid"""
        if isinstance(self.fields, list):
            for f in self.fields:
                self._mark_invalid(invalids, f)
        else:
            self._mark_invalid(invalids, self.fields)

    def _mark_invalid(self, invalids, marks):
        """Only mark invalid on a set list"""
        if not marks:
            return
        for fname in marks.keys():
            widget = self.if_widget(fname+'_label')
            marked = self._marked.get(fname, None)
            if fname in invalids and not marked:
                self._marked[fname] = widget.get_label()
                widget.set_label(
                        "<span color='red'>*%s</span>" % self._marked[fname])
            elif fname not in invalids and marked:
                widget.set_label(self._marked.pop(fname))

    def cancel(self, widget=None):
        """We didn't like what we did, so don't apply"""
        self.done = False
        self.destroy()
        return widget

    

