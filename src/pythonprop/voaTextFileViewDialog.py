#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voaTextFileViewDialog
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

# Dialog box that displays the contents of a voacap circuit prediction

import sys
import os
from gi.repository import Pango

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GObject
except:
    pass
try:
    from gi.repository import Gtk
#    import Gtk.glade
except:
    sys.exit(1)

class VOATextFileViewDialog:

    """GUI to display the result of a voacap circuit prediction"""
    # todo set the users itshfdata directory.  todo mofify to suit windows as well...
    # todo maybe read it as an argument in case we can't guess it...
    itshfbc_path = os.path.expanduser("~")+os.sep+'itshfbc'

    file = ''

    # http://www.rexx.com/~dkuhlman/python_201/python_201.html#SECTION008210000000000000000
    def __init__(self, file=None, datadir="", parent=None):
        self.file=file
        self.datadir=datadir
        self.parent=parent


    def run(self):
        """This function will show the site selection dialog"""

        self.ui_file = os.path.join(self.datadir, "ui", "voaTextFileViewDialog.ui")
        self.wTree = Gtk.Builder()
        self.wTree.add_from_file(self.ui_file)

        self.get_objects("text_file_view_dialog",
                            "text_view",
                            "text_buffer",
                            "save_button",
                            "ok_button")
        self.save_button.connect("clicked", self.on_save_clicked)

        self.text_file_view_dialog.set_transient_for(self.parent)
        self.text_view.modify_font(Pango.FontDescription("Luxi Mono 10"))
        self.results_text = open(self.file, "r").read().replace('\f','')

        try:
            self.text_buffer.set_text(self.results_text)
        except:
            print(_('Failed to read file: '), self.file)

        self.result = self.text_file_view_dialog.run()
        self.text_file_view_dialog.destroy()
        return None


    def get_objects(self, *names):
        for name in names:
            widget = self.wTree.get_object(name)
            if widget is None:
                raise ValueError(_("Widget '%s' not found") % name)
            setattr(self, name, widget)


    def on_save_clicked(self, widget):
        print("in the save dialog")
        dialog = Gtk.FileChooserDialog("Please choose a file", self.parent,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        #self.add_filters(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            try:
                file = open(dialog.get_filename(), "w")
                file.write(self.results_text)
                file.close()
                success_dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK, "File Saved")
                success_dialog.format_secondary_text(
                    "File saved as {:s}.".format(file.name))
                success_dialog.run()
                success_dialog.destroy()
            except:
                error_dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "Error")
                error_dialog.format_secondary_text(
                    "Error saving data to {:s}".format(file.name))
                error_dialog.run()
                error_dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()
