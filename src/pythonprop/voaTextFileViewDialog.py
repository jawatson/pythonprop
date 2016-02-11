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

        #load the dialog from the glade file
        #self.uifile = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voaTextFileViewDialog.ui")
        self.ui_file = os.path.join(self.datadir, "ui", "voaTextFileViewDialog.ui")
        #self.wTree = Gtk.Builder.new_from_file(self.ui_file)
        self.wTree = Gtk.Builder()
        self.wTree.add_from_file(self.ui_file)

        self.get_objects("text_file_view_dialog",
                            "text_view",
                            "text_buffer",
                            "save_button",
                            "ok_button")
        self.text_file_view_dialog.set_transient_for(self.parent)
        self.text_view.modify_font(Pango.FontDescription("Luxi Mono 10"))

        try:
            self.text_buffer.set_text(open(self.file, "r").read().replace('\f',''))
        except:
            print(_('Failed to read file: '), self.file)

        #Create event dictionay and connect it
#        event_dic = { "on_map_eventbox_button_release_event" : self.set_location_from_map,
#                        "on_lat_entry_insert_text" : lat_validator.entry_insert_text,
#                        "on_lon_entry_insert_text" : lon_validator.entry_insert_text,
#                        "on_lat_entry_focus_out_event" : self.update_locator_ui,
#                        "on_lon_entry_focus_out_event" : self.update_locator_ui}

#        self.wTree.connect_signals(event_dic)

        # The locator widgets need to be connected individually.  The handlerIDs are
        # used to block signals when setting the loctaor widget programatically


        self.result = self.text_file_view_dialog.run()
        self.text_file_view_dialog.destroy()
#        self.return_location.set_name(self.name_entry.get_text())
#        self.return_location.set_latitude(float(self.lat_entry.get_text()))
#        self.return_location.set_longitude(float(self.lon_entry.get_text()))
#        return self.result,self.return_location
        return None



    def get_objects(self, *names):
        for name in names:
            widget = self.wTree.get_object(name)
            if widget is None:
                raise ValueError(_("Widget '%s' not found") % name)
            setattr(self, name, widget)
