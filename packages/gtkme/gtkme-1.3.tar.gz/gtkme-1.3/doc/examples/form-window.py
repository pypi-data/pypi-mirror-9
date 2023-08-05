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
A special child window is called the FormWindow, it controls a GtkNotebook
as if each tab was a page in a multi-page form. All data in the form is
collected automatically and can even be verified using a data structural
varification module.

The form window requires specific glade widgets to exist with specific ids
unlike any other window. You must have a set of buttons:

 'next' with signal 'next_page' when clicked
 'previous' with signal 'previous_page' when clicked
 'apply' is optional with 'apply' when clicked

You must also create a GtkNotebook called 'pages' with any settings you like.

"""

import os
import sys
import logging

# Directories where gtkme can be found locally
sys.path.insert(1, '../../lib')
sys.path.insert(1, './lib')

# Import FormWindow like any other window
from gtkme import FormWindow, GtkApp, TreeView


class AppFormWindow(FormWindow):
    """Normal window like any other"""
    name = 'formapp'

    # We need to force this form to be primary as it's normally
    # a ChildWindow and expects to be loaded by the main window
    primary = True

    # Each form has a set of fields which can be gathered together
    # and then validated, defining those fields allows us to skip
    # manually grabbing all the data with the get_data function.
    fields = \
    [ { # Page 1
        'age'      : { 'maxLength': 3, 'minLength': 1, 'type': 'integer' },
        'postcode' : { 'maxLength': 20, 'minLength': 0 }, # default type is string
        'gender'   : { 'maxLength': 40, 'minLength': 0, 'enumeration': ['-','M','F'] }, # XSD enum rules are awesome
    },{ # Page 2
        'password' : { 'maxLength': 200, 'minLength': 6, },
        'confirm'  : { 'maxLength': 200, 'minLength': 6, 'match': 'password' }, # XSD matching rules are cool
        'email'    : { 'maxLength': 200, 'minLength': 0, 'pattern' : '.+@.+\..+' }, # XSD regex rules are hot
    },{ # Page 3
        'sex'      : { 'type' : 'boolean' },
        'flux'     : { 'type' : 'boolean' },
        'wax'      : { 'type' : 'boolean' },
    } ]

    def load_widgets(self):
        # Glade doesn't handle it's own comboboxes with it's own liststore
        # that we define inside glade-3, basically I'm surprised glade manages
        # to put on it's shoes in the morning without exploading a passing goat.
        self.a = TreeView(self.widget('field_gender'), liststore=self.widget('genders'))

    def get_data(self):
        # We can manually gather together data here if needed.
        return FormWindow.get_data(self) # But we won't


class FormWindowApp(GtkApp):
    glade_dir = './'
    app_name = 'formapp'
    windows = [ AppFormWindow ]


def data_output(**data):
    """When windows finish they can call back and deliver any data
    that the window might have collected. In the cae of the Form
    Window that is all the data from the input elements."""
    print data


if __name__ == '__main__':
    try:
        app = FormWindowApp(start_loop=True, callback=data_output)
    except KeyboardInterrupt:
        logging.info("User Interputed")
    logging.debug("Exiting Application")





