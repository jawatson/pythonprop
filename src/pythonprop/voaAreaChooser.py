#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voaAreaChooser
#
# Copyright (c) 2009 J.Watson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  
# 02110-1301, USA.

# Dialog box that returns a VOAAreaRect defining the area 
# for the prediction.

import os
import re
import sys
import math
import cairo

from copy import deepcopy

from voaAreaRect import *

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GObject, Gdk, Gtk, GdkPixbuf
except:
    sys.exit(1)

class VOAAreaChooser:
    """GUI to select tx/rx locations fromVOAArea Input Files"""
    
    def __init__(self, rect=VOAAreaRect(), map_size=(), parent=None,  datadir=""):
        self.datadir = datadir
        self.return_rect = deepcopy(rect)
        self.map_size = map_size
        self.startx = 0
        self.starty = 0
        self.start_lat = 0
        self.start_lon = 0

        self.img_offset_x = 0
        self.img_offset_y = 0
           
        #self.uifile = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voaAreaChooser.ui")
        self.ui_file = os.path.join(self.datadir, "ui", "voaAreaChooser.ui")
        #self.wTree = Gtk.Builder.new_from_file(self.ui_file)
        self.wTree = Gtk.Builder()
        self.wTree.add_from_file(self.ui_file)

        self.get_objects("area_chooser_dialog", "map_eventbox", "select_all_button",
                            "ne_lat_spinbutton", "ne_lon_spinbutton",
                            "sw_lat_spinbutton", "sw_lon_spinbutton")

        self.area_chooser_dialog.set_transient_for(parent)

        #map_file = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "map.jpg")
        map_file = os.path.join(self.datadir, "ui", "map.jpg")
        # the original clean pixbuf map
        self.o_pixbuf = GdkPixbuf.Pixbuf.new_from_file(map_file)

        w, h = self.o_pixbuf.get_width(), self.o_pixbuf.get_height()
        #if not self.map_size:
        self.map_size = (w,h)

        self.map_image = Gtk.Image.new_from_pixbuf(self.o_pixbuf)
        
        self.map_image.set_size_request(w,h) # to shrink to original size (doesn't seem to work with G3)
        
        self.map_eventbox.add(self.map_image) 
        self.map_eventbox.set_size_request(w,h)
        
        #self.map_image.connect('show', self.resize_image) # this was the expose event in the original
        
        # Event signals
        self.map_eventbox.connect("motion_notify_event", self.motion_notify_event)
        self.map_eventbox.connect("button_press_event", self.button_press_event)
        self.map_eventbox.connect("button_release_event", self.button_release_event)
        self.map_eventbox.connect("size_allocate", self.resize_image)        

        self.map_eventbox.set_events(Gdk.EventMask.EXPOSURE_MASK
                            | Gdk.EventMask.LEAVE_NOTIFY_MASK
                            | Gdk.EventMask.BUTTON_PRESS_MASK
                            | Gdk.EventMask.POINTER_MOTION_MASK
                            | Gdk.EventMask.POINTER_MOTION_HINT_MASK)
        # Setup spinbutton & 'Select All' button events
        event_dic = {   "spinbutton_value_changed" : self.do_spinbutton_value_change,
                        "on_select_all_button_clicked" : self.do_select_all
                        }
        self.wTree.connect_signals(event_dic)
        

    def run(self):
        """This function sets up and displays a dialog used to specify the prediction area."""  
 
        self.map_image.show()
        self.draw_voaarearect(self.return_rect) #Sets up the map
        self.update_spinbuttons(self.return_rect)

        while 1:
            response = self.area_chooser_dialog.run()
            if response == -1: continue # -1 response for select_all, dialog remains open
            self.area_chooser_dialog.destroy()
            return response, self.return_rect, self.map_size


    def draw_voaarearect(self, rect):
        """ A thin wrapper around draw_rect function that accepts VOAAreaRect objects."""
        self.startx, self.starty = self.location2map_point(rect.get_sw_lat(), rect.get_sw_lon())
        lat, lon = self.location2map_point(rect.get_ne_lat(), rect.get_ne_lon())
        self.draw_rect(lat,lon)  


    def draw_rect(self, x, y):
        # get a clean pixbuf and set it's size as indicated by map_size
        w,h = self.map_size
        pixbuf = self.o_pixbuf.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR)

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        cc = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(cc, pixbuf, 0, 0)
        cc.paint()

        cc.rectangle(min(x, self.startx), 
                min(y, self.starty), 
                abs(x - self.startx), 
                abs(y - self.starty))
        cc.set_source_rgb(1, 0, 0)
        cc.set_line_width (2)
        cc.stroke() 
        pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, w, h)
        self.map_image.set_from_pixbuf(pixbuf)


    def button_press_event(self, widget, event):
        # Set the first corner of the rectangle
        x_max, y_max = self.map_size
        if event.button == 1:
            self.set_spinbuttons_sensitive(False) 
            x = event.x - ((self.map_eventbox.get_allocation().width - x_max)/2)                       
            self.start_lat, self.start_lon = self.map_point2location(x, event.y)
            self.startx = int(x)
            self.starty = int(event.y)
            self.draw_rect(int(x), int(event.y))
        return True


    def button_release_event(self, widget, event):
        #indictes the rect is complete.  re-enable the
        #spinbuttons and update return_rect
        x_max, y_max = self.map_size
        if event.button == 1:
            self.set_spinbuttons_sensitive(True) 
            # The following line doesn't seem to be required in Gnome 3.8 but was
            # necessary when testing in Gnome 3.6 (Ubuntu 13.04)
            # It can probably be removed in future
            x = event.x - ((self.map_eventbox.get_allocation().width - x_max)/2.0)        
            lat, lon = self.map_point2location(event.x, event.y)
            self.return_rect = VOAAreaRect(self.start_lat, self.start_lon, lat, lon)
            self.update_spinbuttons(self.return_rect)
        return True


    def motion_notify_event(self,widget, event):
        x_max, y_max = self.map_size

        if event.is_hint:
            ptr_window, x, y, state = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.get_state()
        x = x - ((self.map_eventbox.get_allocation().width - x_max)/2)
        if state & Gdk.ModifierType.BUTTON1_MASK:# and pixmap != None:
            if ((0 <= x <= x_max) and (0 <= y <= y_max)):
                self.draw_rect(x, y)
        return False    


    def set_spinbuttons_sensitive(self, sensitive): 
        self.ne_lat_spinbutton.set_sensitive(sensitive)
        self.ne_lon_spinbutton.set_sensitive(sensitive)
        self.sw_lat_spinbutton.set_sensitive(sensitive)
        self.sw_lon_spinbutton.set_sensitive(sensitive)


    def resize_image(self, widget, rect):
        new_w = rect.width
        new_h = rect.height

        if self.map_size == (new_w, new_h): return False
        self.map_size = (new_w, new_h)
        self.draw_voaarearect(self.return_rect) # this sets up self.map_image
        return False


    def location2map_point(self, lat, lon):
        w,h = self.map_size
        pw = ((lon + 180.0) / 360.0) * w
        ph = abs( ((lat - 90.0) / 180.0) * h)
        return (int(pw), int(ph))


    def map_point2location(self, x_coord, y_coord):
        w,h = self.map_size
        lon = ((x_coord/w) * 360.0) - 180.0
        lat = 90.0 - ((y_coord/h) * 180.0) 
        return (lat,lon)       


    def update_spinbuttons(self, area):
        sw_lat, sw_lon, ne_lat, ne_lon = area.get_rect()
        self.sw_lat_spinbutton.set_range(-90.0, ne_lat)
        self.sw_lon_spinbutton.set_range(-180.0, ne_lon)
        self.ne_lat_spinbutton.set_range(sw_lat, 90.0)
        self.ne_lon_spinbutton.set_range(sw_lon, 180.0)

        self.ne_lat_spinbutton.set_value(ne_lat)
        self.ne_lon_spinbutton.set_value(ne_lon)
        self.sw_lat_spinbutton.set_value(sw_lat)
        self.sw_lon_spinbutton.set_value(sw_lon)


    def do_spinbutton_value_change(self, widget):
        value = widget.get_value()
        if widget == self.sw_lat_spinbutton :
            self.return_rect.set_sw_lat(value)
            self.ne_lat_spinbutton.set_range(value, 90.0)
        elif widget == self.sw_lon_spinbutton :
            self.return_rect.set_sw_lon(value)
            self.ne_lon_spinbutton.set_range(value, 180.0)
        elif widget == self.ne_lat_spinbutton : 
            self.return_rect.set_ne_lat(value)
            self.sw_lat_spinbutton.set_range(-90.0, value)
        elif widget == self.ne_lon_spinbutton : 
            self.return_rect.set_ne_lon(value)
            self.sw_lon_spinbutton.set_range(-180.0, value)
        self.draw_voaarearect(self.return_rect)


    def do_select_all(self, widget):
        self.return_rect = VOAAreaRect(-90.0, -180.0, 90.0, 180.0) 
        self.update_spinbuttons(self.return_rect)
        

    def get_objects(self, *names):
        for name in names:
            widget = self.wTree.get_object(name)
            if widget is None:
                raise ValueError, _("Widget '%s' not found") % name
            setattr(self, name, widget)
    
