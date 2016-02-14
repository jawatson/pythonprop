#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voaPlotWindow.py
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
#
# todo consider using a scrolled pane here...
# add buttons to move between plots
# double clicking an all plot should zoom in to an individual plot

import os
import sys
from gi.repository import GObject
from gi.repository import Gtk

class VOAPlotWindow():

    PLOT_RESPONSE_PRINT = 100
    PLOT_RESPONSE_SAVE = 101
    PLOT_RESPONSE_CLOSE = 102

    def __init__(self, title, canvas, parent=None, dpi=150):
        self.dpi = dpi
        self.parent = parent
        self.canvas = canvas

        if not self.parent:
            self.win = Gtk.Window()

            self.ui_file = os.path.join('/usr/local/share/pythonprop', "ui", "voaPropWindowBox.ui")
            self.wTree = Gtk.Builder()
            self.wTree.add_from_file(self.ui_file)
            self.get_objects("main_box", "save_button", "close_button")

            self.main_box.pack_end(self.canvas, True, True, 0)
            self.win.add(self.main_box)

            #self.print_button.connect("clicked", self.print_button_clicked)
            self.save_button.connect("clicked", self.save_button_clicked)
            self.close_button.connect("clicked", self.close_button_clicked)
            self.win.connect("delete-event", Gtk.main_quit)

            self.win.set_default_size(700, 600)
            self.win.show_all()
            Gtk.main()
        else:
            self.win = Gtk.Dialog(title, parent=self.parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT)
            #Gtk.STOCK_PRINT, self.PLOT_RESPONSE_PRINT,
            self.win.add_buttons(
                            Gtk.STOCK_SAVE, self.PLOT_RESPONSE_SAVE,
                            Gtk.STOCK_CLOSE, self.PLOT_RESPONSE_CLOSE)
            self.win.vbox.pack_start(self.canvas, True, True, 0)
            self.win.set_default_size(700, 600)
            #self.win.set_transient_for(self.parent)
            self.win.show()
            response = None
            while response != self.PLOT_RESPONSE_CLOSE and response != Gtk.ResponseType.DELETE_EVENT:
                response = self.win.run()
                if response == self.PLOT_RESPONSE_SAVE:
                    self.save_button_clicked(None)
                elif response == self.PLOT_RESPONSE_PRINT:
                    self.print_button_clicked(None)
            self.close_button_clicked(None)


    def print_button_clicked(self, widget):
        # https://github.com/davidmalcolm/pygobject/blob/master/demos/gtk-demo/demos/printing.py
        pass


    def close_button_clicked(self, widget):
        self.win.destroy()
        if not self.parent:
            Gtk.main_quit
            sys.exit(0)


    def save_button_clicked(self, widget):
        plot_parent = self.parent if self.parent else self.win

        chooser = Gtk.FileChooserDialog(_("Save Image..."),
                plot_parent,
                Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        filter = Gtk.FileFilter()
        filter.set_name("PNG Images")
        filter.add_mime_type("image/png")
        filter.add_pattern("*.png")
        chooser.add_filter(filter)
        save_response = chooser.run()
        if save_response == Gtk.ResponseType.OK:
            save_file = chooser.get_filename()
            if not save_file.endswith('.png'):
                save_file = save_file + '.png'
            self.save_plot(self.canvas, save_file)
        chooser.destroy()


    def save_plot(self, canvas, filename=None):
        canvas.print_figure(filename, dpi=self.dpi, facecolor='white', edgecolor='white')

    def get_objects(self, *names):
        for name in names:
            widget = self.wTree.get_object(name)
            if widget is None:
                raise ValueError(_("Widget '%s' not found") % name)
            setattr(self, name, widget)
