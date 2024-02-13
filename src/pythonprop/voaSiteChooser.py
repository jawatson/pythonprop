#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voacapSiteChooser
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

# Dialog box that returns a voaLocation

import os
import re
import sys
import itertools
import cairo

from .hamlocation import *
from .treefilebrowser import *

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GObject, Gtk, Gdk
except:
    sys.exit(1)

class VOASiteChooser:
    
    """GUI to select tx/rx locations fromVOAArea Input Files"""

    lcase_letters = list(map(chr, list(range(97, 123))))
    ucase_letters = list(map(chr, list(range(65, 91))))
    
    def __init__(self, location=HamLocation(), map_size=(), itshfbc_path = '', parent=None, datadir=""):
        self.datadir = datadir
        # Delete any trailing locator from the site name
        #_name = location.get_name()
        #_loc = re.compile (r"\[\D\D\d\d\D\D\]\s*$")
        #if re.search(_loc, _name):
        #    print "found locator"
        #self.locator_append_checkbutton.set_state(re.search(_loc, _name))
        #location.set_name(_loc.split(_name)[0])
        self.return_location = location
        #self.map_size = map_size #todo allow the dialog size to be saved
        
        #load the dialog from the glade file      
        #self.uifile = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voaSiteChooser.ui")
        self.ui_file = os.path.join(self.datadir, "ui", "voaSiteChooser.ui")
        #self.wTree = Gtk.Builder.new_from_file(self.ui_file)
        self.wTree = Gtk.Builder()
        self.wTree.add_from_file(self.ui_file)

        self.get_objects("site_chooser_dialog", "map_eventbox", "map_aspectframe",
                                "lat_spinbutton", "lon_spinbutton", "name_entry", 
                                "locator_combo1", "locator_combo2", "locator_combo3",
                                "locator_combo4", "locator_combo5", "locator_combo6",
                                "locator_append_checkbutton", "geo_tv", "file_tv")

        self.site_chooser_dialog.set_transient_for(parent)
        # put the image from pixbuf, to make it resizable
        self.map_image_aspect_ratio = None
        
        #map_file = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "map.jpg")
        map_file = os.path.join(self.datadir, "ui", "map.jpg")
       
        # the original clean pixbuf map
        self.o_pixbuf = GdkPixbuf.Pixbuf.new_from_file(map_file)

        w, h = self.o_pixbuf.get_width(), self.o_pixbuf.get_height()
        #if not self.map_size:
        self.map_size = (w,h)

        self.map_image = Gtk.Image.new_from_pixbuf(self.o_pixbuf)
        self.map_image.set_size_request(w,h) # allow to downsize to map_file original size

        self.map_eventbox.add(self.map_image) 
        self.map_eventbox.set_size_request(w,h)

        self.map_aspectframe.set_size_request(w,h)
                
        points = []
        points.append(self.location2map_point(self.return_location))
        self.set_map_points(points) # this sets up self.map_image

        # Delete any trailing locator from the site name
        _name = location.get_name()
        _loc = re.compile (r"\[\D\D\d\d\D\D\]\s*$")
        if re.search(_loc, _name):
            self.locator_append_checkbutton.set_active(True)
        self.return_location.set_name(_loc.split(_name)[0])
        

        #run the dialog and store the response      
        self.populate_locator_combos()
        self.update_spinbuttons(self.return_location)
        self.set_locator_ui(self.return_location.get_locator())
        self.name_entry.set_text(self.return_location.get_name())

        #Create event dictionary and connect it
        event_dic = { "on_lat_spinbutton_value_changed" : self.update_locator_ui,
                      "on_lon_spinbutton_value_changed" : self.update_locator_ui
                      }
        self.wTree.connect_signals(event_dic)
        self.map_eventbox.connect("size_allocate", self.resize_image)
        self.map_eventbox.connect("button_press_event", self.set_location_from_map)
       

        # The locator widgets need to be connected individually.  The handlerIDs are 
        # used to block signals when setting the locator widget programatically
        
        self.locator_combo1_handler_id = self.locator_combo1.connect("changed", self.set_location_from_locator)
        self.locator_combo2_handler_id = self.locator_combo2.connect("changed", self.set_location_from_locator)
        self.locator_combo3_handler_id = self.locator_combo3.connect("changed", self.set_location_from_locator)
        self.locator_combo4_handler_id = self.locator_combo4.connect("changed", self.set_location_from_locator)
        self.locator_combo5_handler_id = self.locator_combo5.connect("changed", self.set_location_from_locator)
        self.locator_combo6_handler_id = self.locator_combo6.connect("changed", self.set_location_from_locator)
        
        self.locator_combos = ((self.locator_combo1,self.locator_combo1_handler_id), 
                                            (self.locator_combo2, self.locator_combo2_handler_id),
                                            (self.locator_combo3, self.locator_combo3_handler_id), 
                                            (self.locator_combo4, self.locator_combo4_handler_id),
                                            (self.locator_combo5, self.locator_combo5_handler_id), 
                                            (self.locator_combo6, self.locator_combo6_handler_id))
        # Set up the file selection area
        self.tfb = TreeFileBrowser(root = itshfbc_path, view = self.file_tv, file_types = ('*.geo', '*.GEO'))
        self.file_tv.connect("cursor-changed", self.update_geo_tv)
        
        sm = self.geo_tv.get_selection()
        sm.set_mode(Gtk.SelectionMode.SINGLE)
        #sm.set_select_function(self.geo_tv_selected, False) # todo pygobject check this (it's just a guess)
        sm.connect("changed", self.geo_tv_selected)
        
        self.alpha_numeric_re = re.compile(r'[\W_]+')
        self.latitude_column = 0
        self.longitude_column = 0
         

    def run(self):
        """This function runs the site selection dialog""" 
        self.map_image.show() 
        self.result = self.site_chooser_dialog.run()
        _site_name = self.name_entry.get_text()
        if self.locator_append_checkbutton.get_active():
            _site_name = _site_name + ' ['+self.return_location.get_locator()+']'
        self.return_location.set_name(_site_name)
        self.site_chooser_dialog.destroy()
        return self.result, self.return_location, self.map_size
        
        
    def set_map_points(self, points=[]):
        # points is a list of tuples (x, y)
        w,h = self.map_size
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        cc = cairo.Context(surface)
        cc.set_line_width(1.)
        scaled_pixbuf = self.o_pixbuf.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR)
        Gdk.cairo_set_source_pixbuf(cc, scaled_pixbuf, 0, 0)
        cc.paint()
        
        radius = 6 if (w / 200.0) < 3 else int(round(w/200.0))

        for point in points:
            cc.arc(point[0], point[1], radius, 0., 2 * math.pi)
            cc.move_to(point[0] - 6 - radius,  point[1])
            cc.line_to(point[0] + 6 + radius,  point[1])
            cc.move_to(point[0], point[1] - 6 - radius)
            cc.line_to(point[0], point[1] + 6 + radius)
            cc.set_source_rgb(1, 0, 0)
            cc.stroke()
        pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, w, h)
        self.map_image.set_from_pixbuf(pixbuf)


    def resize_image(self, widget, rect):
        new_w = rect.width
        new_h = rect.height

        if self.map_size == (new_w, new_h):
            return False
        self.map_size = (new_w, new_h)
        points = []
        points.append(self.location2map_point(self.return_location))
        self.set_map_points(points) # this sets up self.map_image
        return False


    def populate_locator_combos(self):
        #todo check that this is actually required, combos are also being 
        #populated in the .ui file
        self.populate_combo(self.locator_combo1, list(map(chr, list(range(65, 83)))))
        self.populate_combo(self.locator_combo2, list(map(chr, list(range(65, 83)))))
        self.populate_combo(self.locator_combo3, list(map(chr, list(range(48, 58)))))
        self.populate_combo(self.locator_combo4, list(map(chr, list(range(48, 58)))))
        self.populate_combo(self.locator_combo5, list(map(chr, list(range(97, 121)))))
        self.populate_combo(self.locator_combo6, list(map(chr, list(range(97, 121)))))
        
        
    def populate_combo(self, cb, list):
        list_model = Gtk.ListStore(GObject.TYPE_STRING) 
        for af in list:
            list_model.append([af])
        cb.set_model(list_model)
        cell = Gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 0)
        #cb.set_wrap_width(20)
        cb.set_active(0)    

        
    # Function called when the lat/lon is changed in the entry boxes
    def update_locator_ui(self, widget):
        if widget == self.lat_spinbutton:
            self.return_location.set_latitude(self.lat_spinbutton.get_value())
        elif widget == self.lon_spinbutton:
            self.return_location.set_longitude(self.lon_spinbutton.get_value())
        self.block_locator_combos(True)
        self.set_locator_ui(self.return_location.get_locator())
        points = [self.location2map_point(self.return_location)]
        self.set_map_points(points)
        self.block_locator_combos(False)            
        # Unblock the locator combo signals
        

    def block_locator_combos(self, block):
        if (block):
            for combo, handler in self.locator_combos:
                combo.handler_block(handler)
        else:
            for combo, handler in self.locator_combos:
                combo.handler_unblock(handler)                                  
        
    # Updates the locator UI elements to the argument passed in 'locator'
    # todo some error checking would be nice....
    def set_locator_ui(self, locator):
        locator = locator.upper()
        self.locator_combo1.set_active(self.ucase_letters.index(locator[0]))
        self.locator_combo2.set_active(self.ucase_letters.index(locator[1]))    
        self.locator_combo3.set_active(int(locator[2]))
        self.locator_combo4.set_active(int(locator[3]))                     
        # todo make this an 'if' in case we get a four digit locator    
        self.locator_combo5.set_active(self.ucase_letters.index(locator[4]))
        self.locator_combo6.set_active(self.ucase_letters.index(locator[5]))    

    def location2map_point(self, location):
        w,h = self.map_size
        lat = location.get_latitude()
        lon = location.get_longitude()
        pw = ((lon + 180.0) / 360.0) * w
        ph = abs( ((lat - 90.0) / 180) * h)
        return (int(round(pw)), int(round(ph)))

    def set_location_from_map(self, widget, event):
        w, h = self.map_size
        x = event.x - ((self.map_eventbox.get_allocation().width - w)/2)                       
        #if not (w > x > 0)  or not (h > event.y > 0): return  # out of map bounds
        if ((0 <= x <= w) and (0 <= event.y <= h)):
            lon = ((x/w) * 360.0) - 180.0
            lat = 90.0 - ((event.y/h) * 180)
            self.return_location.set_latitude_longitude(lat, lon)
            self.update_spinbuttons(self.return_location)
            self.set_locator_ui(self.return_location.get_locator())
            # redraw-point
            points = [(int(x), int(event.y))]
            self.set_map_points(points)
        

    def set_location_from_locator(self, widget):
        loc = ''        
        for cb, handlerID in self.locator_combos:
            loc = loc + self.get_active_text(cb)
        self.return_location.set_locator(loc)
        self.update_spinbuttons(self.return_location)
        points = [self.location2map_point(self.return_location)]
        self.set_map_points(points)
        
        
    def update_spinbuttons(self,location):
        self.lat_spinbutton.set_value(location.get_latitude())
        self.lon_spinbutton.set_value(location.get_longitude())
        self.name_entry.set_text(location.get_name())
    
    
    def get_active_text(self, combobox):
        model = combobox.get_model()
        active = combobox.get_active()
        if active < 0:
            return ''
        return model[active][0]

    ####################################################
    # File Selection methods follow
    ####################################################
    def update_geo_tv(self, file_chooser):
        filename = self.tfb.get_selected()
        try:
            if filename.endswith('.geo'):
                f = open(filename)
                header_is_defined = False
                for line in f:
                    if line.startswith('|'):
                        start_index = 0
                        end_index = 0
                        headers = []
                        while end_index >= 0:
                            end_index = line.find('|', start_index)
                            heading = line[start_index:end_index].strip()
                            heading = re.sub(r'=', '', heading)
                            heading = heading.title()
                            if len(heading) > 0:
                                headers.append((heading, int(start_index)-1, int(end_index), len(headers)))
                            start_index = end_index + 1
                        self.geo_model = Gtk.ListStore(*([str] * len(headers)))
                        self.build_geo_tv(headers)
                        header_is_defined = True
                    elif header_is_defined:
                        try:
                            row = []
                            for column in headers:
                                row.append((line[column[1]:column[2]]).strip())
                            self.geo_model.append(row)       
                        except:
                            print('Failed to read line: ', line)
                            print('with error ',sys.exc_info())
                f.close()
                self.geo_tv.set_model(self.geo_model)
        except:
            pass
            #print 'Error parsing geo file.'
            #print sys.exc_info()
            try:
                self.geo_model.clear()
            except AttributeError:
                pass
        return

    
    def remove_all_tv_columns(self, tv):
        columns = tv.get_columns()
        for col in columns:
            tv.remove_column(col)


    def build_geo_tv(self, headers):
        self.remove_all_tv_columns(self.geo_tv)
        for column in headers:
            title = column[0]
            cell = Gtk.CellRendererText()
            cell.set_property('xalign', 1.0)
            tvcol = Gtk.TreeViewColumn(title, cell)
            tvcol.add_attribute(cell, 'text' , int(column[3]))
            if title.startswith('Lat'):
                self.latitude_column = int(column[3])
            elif title.startswith('Lon'):
                self.longitude_column = int(column[3])
            tvcol.set_resizable(True)
            tvcol.set_reorderable(True)
            tvcol.set_sort_column_id(int(column[3]))
            self.geo_tv.append_column(tvcol)


    def geo_tv_selected(self, selection):
        #http://python-gtk-3-tutorial.readthedocs.org/en/latest/treeview.html#the-selection
        model, geo_iter = selection.get_selected()
        if geo_iter != None:
            title = ''
            for col in range(0, self.geo_model.get_n_columns()):
                if col == self.latitude_column:
                    self.return_location.set_latitude(self.get_decimal_coordinate(self.geo_model.get_value(geo_iter, col)))
                elif col == self.longitude_column:
                    self.return_location.set_longitude(self.get_decimal_coordinate(self.geo_model.get_value(geo_iter, col)))
                else:
                    title = title + ' ' + self.geo_model.get_value(geo_iter, col)
            self.return_location.set_name(title)
            self.update_spinbuttons(self.return_location)        


    def get_decimal_coordinate(self, ll):
        val = ll.split()
        dec = float(val[0]) + float(val[1])/60.0
        if ((val[2] == 'S') or (val[2] == 'W')):
            dec = -dec
        return dec
        
        
    def get_objects(self, *names):
        for name in names:
            widget = self.wTree.get_object(name)
            if widget is None:
                raise ValueError(_("Widget '%s' not found") % name)
            setattr(self, name, widget)

