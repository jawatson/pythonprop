#! /usr/bin/env python
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
try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GObject
except:
    pass
try:
    from gi.repository import Gtk
except:
    sys.exit(1)

class VOAPlotWindow():

    def __init__(self, title, canvas, parent=None, dpi=150):
        self.dpi = dpi
        self._dia = Gtk.Dialog(title, parent=parent, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT)
        self._dia.add_buttons(Gtk.STOCK_SAVE, Gtk.ResponseType.OK, Gtk.STOCK_CLOSE, Gtk.ResponseType.NONE)
        self._dia.vbox.pack_start(canvas, True, True, 0)
        self._dia.set_default_size(700, 600)
        self._dia.show()

        _response = None
        while _response != Gtk.ResponseType.NONE and _response != Gtk.ResponseType.DELETE_EVENT:
            _response = self._dia.run()
            if _response == Gtk.ResponseType.OK:
                _chooser = Gtk.FileChooserDialog(_("Save Image..."),
                                        parent,
                                        Gtk.FileChooserAction.SAVE,
                                        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
                _filter = Gtk.FileFilter()
                _filter.set_name("PNG Images")
                _filter.add_mime_type("image/png")
                _filter.add_pattern("*.png")
                _chooser.add_filter(_filter)
                _save_response = _chooser.run()
                if _save_response == Gtk.ResponseType.OK:
                    save_file = _chooser.get_filename()
                    if not save_file.endswith('.png'):
                        save_file = save_file + '.png'
                    self.save_plot(canvas, save_file)
                _chooser.destroy()
        self._dia.destroy()
        
        
    def save_plot(self, canvas, filename=None):
        canvas.print_figure(filename, dpi=self.dpi, facecolor='white', edgecolor='white')

