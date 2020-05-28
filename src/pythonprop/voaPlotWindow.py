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

"""
Some useful printing references;

http://askubuntu.com/questions/220350/how-to-add-a-print-dialog-to-an-application
https://developer.gnome.org/gtk3/stable/GtkPrintUnixDialog.html
http://nullege.com/codes/search/gi.repository.Gtk.PrintOperationAction.PRINT_DIALOG
https://github.com/GNOME/pygobject/blob/master/demos/gtk-demo/demos/printing.py

printing pngs with python
http://stackoverflow.com/questions/10983739/how-to-composite-multiple-png-into-a-single-png-using-gtk-cairo

"""

import os
import sys
from gi.repository import GObject
from gi.repository import Gtk

from .voaPlotFilePrinter import VOAPlotFilePrinter

class VOAPlotWindow():

    PLOT_RESPONSE_PRINT = 100
    PLOT_RESPONSE_SAVE = 101
    PLOT_RESPONSE_CLOSE = 102

    def __init__(self,
            title,
            canvas,
            parent=None,
            dpi=150,
            datadir=None):
        self.dpi = dpi
        self.parent = parent
        self.canvas = canvas

        if not self.parent:
            self.win = Gtk.Window()

            self.ui_file = os.path.join(datadir, "ui", "voaPropWindowBox.ui")

            self.wTree = Gtk.Builder()
            self.wTree.add_from_file(self.ui_file)
            self.get_objects("main_box", "print_button", "save_button", "close_button")

            self.main_box.pack_end(self.canvas, True, True, 0)
            self.win.add(self.main_box)

            self.print_button.connect("clicked", self.print_button_clicked)
            self.save_button.connect("clicked", self.save_button_clicked)
            self.close_button.connect("clicked", self.close_button_clicked)
            self.win.connect("delete-event", Gtk.main_quit)

            self.win.set_default_size(700, 600)
            self.win.show_all()
            Gtk.main()
        else:
            self.ui_file = os.path.join(datadir, "ui", "voaPlotDisplayDialog.ui")

            self.wTree = Gtk.Builder()
            self.wTree.add_from_file(self.ui_file)
            self.get_objects("plot_display_dialog", "print_button", "save_button", "close_button")
            
            #self.win = Gtk.Dialog(title, parent=self.parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT)
            
            self.plot_display_dialog.show()
            response = None
            while response != self.PLOT_RESPONSE_CLOSE and response != Gtk.ResponseType.DELETE_EVENT:
                response = self.win.run()
                if response == self.PLOT_RESPONSE_SAVE:
                    self.save_button_clicked(None)
                elif response == self.PLOT_RESPONSE_PRINT:
                    self.print_button_clicked(None)
            self.close_button_clicked(None)


    def print_button_clicked(self, widget):
        p = VOAPlotFilePrinter(self.canvas)
        print_parent = self.parent if self.parent else self.win
        p.run(print_parent)


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
