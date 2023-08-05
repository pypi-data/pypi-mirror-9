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
Sample Application using interesting pixmaps
"""

import os
import sys
import logging

sys.path.insert(1, '../../lib')
sys.path.insert(1, './lib')

# Load a Pixmap Manager as well as the normal classes
from gtkme import Window, GtkApp, PixmapManager
from gtkme.pixmap import SizeFilter, OverlayFilter, InternetPixmaps

image2 = 'image'
image1 = 'http://ubunchu.net/images/c1.png'
image3 = 'http://ubunchu.net/images/c2.png'
image4 = 'http://ubunchu.net/images/c3.png'


class TestImages(InternetPixmaps):
    # Where the images are located
    pixmap_dir = './images'
    # Global filters to apply to all images
    filters = [ SizeFilter, OverlayFilter ]


class PixmapWindow(Window):
    """Pixmap example window."""
    name = 'pixmapapp'

    def load_widgets(self):
        # Create a pixmap manager which controls where the images are
        # This can be made into an ineritied class where pixmap_dir is
        # set much like GtkApp and glade_dir or not.
        pix = TestImages('complex', size=128, overlay='overlay', placement=[0,1])

        # We can use the manager directly, or it can be used by lists
        # And other automatic features in gtkme.
        self.widget('image1').set_from_pixbuf(pix.get_pixmap(image1))
        self.widget('image2').set_from_pixbuf(pix.get_pixmap(image2))
        self.widget('image3').set_from_pixbuf(pix.get_pixmap(image3, overlay='other'))
        self.widget('image4').set_from_pixbuf(pix.get_pixmap(image4, overlay='other'))


class PixmapApp(GtkApp):
    """The application is in charge of loading the glade files, loads
    the windows"""
    glade_dir = './'
    app_name = 'pixmapapp'
    windows = [ PixmapWindow ]


if __name__ == '__main__':
    try:
        app = PixmapApp(start_loop=True)
    except KeyboardInterrupt:
        logging.info("User Interputed")
    logging.debug("Exiting Application")





