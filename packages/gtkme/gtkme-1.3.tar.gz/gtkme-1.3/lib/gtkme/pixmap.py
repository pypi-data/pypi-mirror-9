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
Wraps the gtk pixmap access.
"""

import os
import logging

from main import LoopDe
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

import urllib2

ICON_THEME = Gtk.IconTheme.get_default()
BILINEAR = GdkPixbuf.InterpType.BILINEAR


class AnimationManager(LoopDe):
    """Provides a way to animate an image widget
    (useful for please wait... screens)"""
    frame_from = 0
    frames = 1

    @property
    def pixmaps(self):
        raise NotImplementedError("No pixmaps definded for animation.")
    
    def __init__(self, widget):
        if isinstance(self.frames, int):
            self._frames = range(self.frame_from, self.frames)
        else:
            self._frames = self.frames
        self._length = len(self._frames)
        self._target = widget
        self._pos = 0

    def start(self):
        self._pos = self.frame_from
        self._target.show()
        self.loop()

    def loop(self):
        """Run once per thread turn"""
        self._pos += 1
        if self._pos >= self._length:
            self._pos = 0
        frame = str(self._frames[self._pos])
        image = self.pixmaps.get_pixmap(frame)
        self._target.set_from_pixbuf(image)

    def stop(self):
        """run once the thread is finished"""
        self._target.hide()


class PixmapFilter(object):
    """Base class for filtering the pixmaps in a manager's output.
       
       required - List of values required for this filter.

       Use:
       
       class Foo(PixmapManager):
           filters = [ PixmapFilterFoo ]

    """
    required = [ ]

    def __init__(self, manager, **kwargs):
        self.manager = manager
        missing = self.required[:]
        for key in kwargs.keys():
           if key in missing:
               missing.remove(key)
           setattr(self, key, kwargs[key])
        self.enabled = len(missing) == 0
        if not self.enabled:
            self.filter = self.do_nothing

    def do_nothing(self, img, **kwargs):
        """What disabled filters do"""
        return img

    def filter(self, img, **kwargs):
        """Run filter, replace this methodwith your own"""
        raise NotImplementedError("Please add 'filter' method to your PixmapFilter class %s." % type(self).__name__)



class OverlayFilter(PixmapFilter):
    """Adds an overlay to output images, overlay can be any name that
    the owning pixmap manager can find.

    overlay  : Name of overlay image
    location : Location of the image:
      0      - Full size (1 to 1 overlay, default)
      (x,y)  - Percentage from one end to the other position 0-1
    alpha    : Blending alpha, 0 - 255

    """
    overlay = None
    placement = 0
    alpha = 255

    def filter(self, img, overlay=None, **kwargs):
        overlay = overlay or self.overlay
        if overlay != None:
            overlay = self.manager.get(overlay, exempt=True)

            # Default values for full sized overlay
            width = img.get_width()
            height = img.get_height()
            (x, y) = (0, 0)

            if self.placement:
                (x, y, width, height) = self.set_position(overlay, width, height)

            if overlay:
                overlay.composite(img, x, y, width, height, x, y, 1, 1, BILINEAR, self.alpha)
            else:
                logging.warn("Couldn't find overlay '%s'" % self.overlay)
        return img

    def set_position(self, img, width, height):
        """Sets the position of img on the given width and height"""
        w = img.get_width()
        h = img.get_height()
        if w > width or h > height:
            logging.warn("Overlay is to large: %d > %d or %d > %d" % (w, width, h, height))
            return (0, 0, int(width), int(height))
        x = (width - w) * self.placement[0]
        y = (height - h) * self.placement[1]
        return (int(x), int(y), int(w), int(h))


class SizeFilter(PixmapFilter):
    """Resizes images to a certain size:
    
    resize_mode - Way in which the size is calculated
      0 - Best Aspect, don't grow
      1 - Best Aspect, grow
      2 - Cropped Aspect
      3 - Stretch
    """
    required = [ 'size' ]
    resize_mode = 0

    def __init__(self, *args, **kwargs):
        PixmapFilter.__init__(self, *args, **kwargs)
        if self.size:
            if isinstance(self.size, int):
                self.size = (self.size, self.size)
            if not hasattr(self.size, '__iter__') or len(self.size) < 2:
                raise AttributeError("Size needs to be a number or two number tuple.")
            self.w = float(self.size[0])
            self.h = float(self.size[1])

    def aspect(self, w, h):
        if self.resize_mode == 3 or (\
           self.resize_mode == 0 and w < self.w and h < self.h\
           ):
            return (w, h)
        (pw, ph) = (self.w / w, self.h / h)
        factor = self.resize_mode==2 and max(pw, ph) or min(pw, ph)
        return (int(w*factor), int(h*factor))

    def filter(self, img, **kwargs):
        if self.size != None:
            (width, height) = self.aspect(img.get_width(), img.get_height())
            return img.scale_simple(width, height, BILINEAR)
        return img


class PixmapManager(object):
    """Manage a set of cached pixmaps, returns the default image
    if it can't find one or the missing image if that's available."""
    missing_image = None
    default_image = 'default'
    icon_theme = ICON_THEME
    theme_size = 32
    filters = [ SizeFilter ]

    def get_pixmap_dir(self):
        """Set this variable in your class"""
        if not hasattr(self, 'pixmap_dir'):
            raise NotImplementedError("You need to set 'pixmap_dir' in the class.")
        return self.pixmap_dir

    def __init__(self, location, pixmap_dir=None, **kwargs):
        if pixmap_dir:
            self.pixmap_dir = pixmap_dir
        self.location = os.path.join(self.get_pixmap_dir(), location)

        # Add any instance specified filters first
        self._filters = kwargs.get('filters', [])
        for lens in self.filters:
            # Now add any class specified filters with optional kwargs
            # Default: SizeFiler( size=required_field )
            self._filters.append(lens(self, **kwargs))

        self.cache    = {}
        self.get_pixmap(self.default_image)

    def get(self, *args, **kwargs):
        return self.get_pixmap(*args, **kwargs)

    def key_name(self, data):
        try:
            return (True, data.decode('UTF-8'))
        except UnicodeError:
            # Not a name or filename, take some bytes from the end
            try:
                return (False, data[-10:].encode('base64'))
            except UnicodeEncodeError:
                return (True, data)

    def get_pixmap(self, data, exempt=False, **kwargs):
        """Simple method for getting a set of pix pixmaps and caching them."""
        if not data:
            data = self.default_image
        (string, key) = self.key_name(data)

        if not self.cache.has_key(key):
            # load the image from data or a filename/theme icon
            if not string or '<svg' in data:
                self.cache[key] = self.load_from_data(data)
            else:
                self.cache[key] = self.load_from_name(data)

            # Filer the new image if not exempt from such things
            if self.cache[key] and not exempt:
                for lens in self._filters:
                    self.cache[key] = lens.filter(self.cache[key], **kwargs)

        if not self.cache.has_key(key) or not self.cache[key]:
            key = self.default_image
        return self.cache.get(key, self.missing_image)

    def load_from_data(self, data):
        """Load in memory picture file (jpeg etc)"""
        # This doesn't work yet, returns None *shrug*
        loader = GdkPixbuf.PixbufLoader()
        loader.write(data)
        p = loader.get_pixbuf()
        loader.close()
        return p

    def load_from_name(self, name):
        """Load a pixbuf from a name, filename or theme icon name"""
        pixmap_path = self.pixmap_path(name)
        if os.path.exists(pixmap_path):
            try:
                return GdkPixbuf.Pixbuf.new_from_file(pixmap_path)
            except RuntimeError, msg:
                logging.warn("No pixmap '%s', %s" % (pixmap_path, msg))
                return None 
        elif self.icon_theme and self.icon_theme.has_icon(name):
            return self.theme_pixmap(name, size=self.theme_size)
        # Nothing detectable
        if name != self.default_image:
            logging.warning("Can't find pixmap for %s in %s" % (name, self.location))
        return None

    def theme_pixmap(self, name, size=32):
        """Internal user: get image from gnome theme"""
        size = size or 32
        if not self.icon_theme.has_icon(name):
            name = 'image-missing'
        try:
            return self.icon_theme.load_icon(name, size, 0)
        except Exception, error:
            logging.debug("Can't load icon '%s': %s" % (name, str(error)))
            return None

    def pixmap_path(self, name):
        """Returns the pixmap path based on stored location"""
        svg_path = os.path.join(self.location, '%s.svg' % name)
        png_path = os.path.join(self.location, '%s.png' % name)
        if os.path.exists(name) and os.path.isfile(name):
            return name
        if os.path.exists(svg_path) and os.path.isfile(svg_path):
            return svg_path
        elif os.path.exists(png_path) and os.path.isfile(png_path):
            return png_path
        return os.path.join(self.location, name)


class InternetPixmaps(PixmapManager):
    """Provides access to internet images, chached to disk."""
    def __init__(self, *args, **kwargs):
        PixmapManager.__init__(self, *args, **kwargs)
        if not os.access(self.location, os.W_OK):
            raise IOError("Pixmap cache directory '%s' must be writable" % self.location)

    def url_name(self, url):
        return url.split('/')[-1]

    def pixmap_path(self, url):
        """Attempt to download and cache the requested file, return filename"""
        localname = PixmapManager.pixmap_path(self, url)
        if os.path.exists(localname):
            return localname
        filename = self.url_name(url)
        if '/' not in filename:
            filename = os.path.join(self.location, filename)
        if '.' not in filename:
            filename += '.image'
        if os.path.exists(filename):
            return filename
        if url[:7] != 'http://':
            return filename
        with open(filename, 'wb') as fhl:
            try:
                webFile = urllib2.urlopen(url, None, 2)
                result = webFile.read()
            except Exception, error:
                logging.error("Error opening url '%s': %s" % (url, str(error)))
                return None
            webFile.close()
            fhl.write(result)
        return filename

