#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voaAreaPlotgui.py
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

import sys
import os
import datetime
import subprocess

from mpl_toolkits.basemap import Basemap

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

import gettext, locale, sys
GETTEXT_DOMAIN = 'voacapgui'
LOCALE_PATH = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), 'po')

langs = []
lc, enc = locale.getdefaultlocale()
if lc:
    langs = [lc]
language = os.environ.get('LANGUAGE', None)
if language:
    langs += language.split(':')
gettext.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
gettext.textdomain(GETTEXT_DOMAIN)
lang = gettext.translation(GETTEXT_DOMAIN, LOCALE_PATH, languages=langs, fallback=True)
lang.install()#app, local_path)

# glade file
# see http://bugzilla.gnome.org/show_bug.cgi?id=344926 for why the
# next two commands look repeated.
# tod0
#Gtk.glade.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
#Gtk.glade.textdomain(GETTEXT_DOMAIN)
gettext.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
gettext.textdomain(GETTEXT_DOMAIN)


from .voaFile import *
from .voaAreaPlot import *


class VOAAreaPlotGUI:
    """Graphical front end to the voaAreaPlot application"""

    # set the users itshfdata directory.
    # todo mofify to suit windows as well...
    # itshfbc_path = os.path.expanduser("~")+os.sep+'itshfbc'

    plot_type_d = { 1: _('MUFday'),
                    2: _('Reliability'),
                    3: _('SNR'),
#                    4: _('DBW'),
                    }


    cmap_d = {'bone': _('bone'),
              'cool': _('cool'),
              'copper': _('copper'),
              'gray': _('gray'),
              'hot': _('hot'),
              'hsv': _('hsv'),
              'jet': _('jet'),
              'pink': _('pink'),
              'spring': _('spring'),
              'summer': _('summer'),
              'winter': _('winter')}

    def __init__(self, data_source_filename, parent=None, exit_on_close = True, datadir=""):
        self.datadir = datadir
        self.exit_on_close = exit_on_close
        #self.uifile = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voaAreaPlotgui.ui")
        self.parent = parent
        if self.parent:
            self.ui_file = os.path.join(self.datadir, "ui", "voaAreaPlotDialog.ui")
        # todo this should be gtk_builder_new_from_file
        else:
            self.ui_file = os.path.join(self.datadir, "ui", "voaAreaPlotWindow.ui")
        #self.wTree = Gtk.Builder.new_from_file(self.ui_file)
        self.wTree = Gtk.Builder()
        self.wTree.add_from_file(self.ui_file)

        self.get_objects("dialog", "type_combobox", "group_combobox",
                        "tz_spinbutton", "cmap_combobox", "contour_checkbutton",
                        "greyline_checkbutton", "parallels_checkbutton",
                        "meridians_checkbutton")
        if self.parent:
            self.dialog.set_transient_for(self.parent)

        self.dialog.set_title(_("Plot Control"))
        self.populate_combo(self.type_combobox, self.plot_type_d, 'value')
        model = self.type_combobox.get_model()
        iter = model.get_iter_first()
        while iter:
            if model.get_value(iter, 0) == '2': # reliability
                self.type_combobox.set_active_iter(iter)
                break
            iter = model.iter_next(iter)

        self.populate_combo(self.cmap_combobox, self.cmap_d, 'value')
        model = self.cmap_combobox.get_model()
        iter = model.get_iter_first()
        while iter:
            if model.get_value(iter, 0) == 'jet':
                self.cmap_combobox.set_active_iter(iter)
                break
            iter = model.iter_next(iter)

        #todo check the file exists
        if data_source_filename.endswith('.voa'):
            data_source_filename = data_source_filename.split(".voa")[0] #TODO: this needs to be more robust...

        self.in_filename = data_source_filename
        in_file = VOAFile(self.in_filename+'.voa')
        in_file.parse_file()
        self.num_plots = in_file.get_num_plots()
        d = { 0 : _('All Plots'),}
        for i in range(1,self.num_plots+1): d[i] = str(i)
        self.populate_combo(self.group_combobox, d, 'key')

        event_dic = { "on_dialog_destroy" : self.quit_application,
                      "on_cancel_button_clicked" : self.quit_application,
                      "on_ok_button_clicked" : self.run_plot}
        self.wTree.connect_signals(event_dic)
        if self.parent:
            self.dialog.run()
        else:
            self.dialog.show_all()
            Gtk.main()

    def run_plot(self, widget):
#        _color_map = self.cmap_d[self.cmap_combobox.get_active()]
#        _data_type = self.type_combobox.get_active()+1
        _color_map = self.cmap_combobox.get_model().get_value(self.cmap_combobox.get_active_iter(), 0)
        _data_type = self.type_combobox.get_model().get_value(self.type_combobox.get_active_iter(), 0)
        if self.group_combobox.get_active() == 0:
        	_vg_files = list(range(1,self.num_plots+1))
        else:
        	_vg_files = [self.group_combobox.get_active()]
        _time_zone = self.tz_spinbutton.get_value_as_int()
        plot_parent = self.parent if self.parent else self.dialog
        plot = VOAAreaPlot(self.in_filename,
                        data_type = _data_type,
                        vg_files = _vg_files,
                        time_zone = _time_zone,
                        color_map = _color_map,
                        filled_contours = self.contour_checkbutton.get_active(),
                        plot_meridians = self.meridians_checkbutton.get_active(),
                        plot_parallels = self.parallels_checkbutton.get_active(),
                        plot_nightshade = self.greyline_checkbutton.get_active(),
                        parent = plot_parent)
        #self.dialog.run()


    def populate_combo(self, cb, d, sort_by='value'):
        _model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        items = list(d.items())
        if sort_by == 'value':
            items = [(v, k) for (k, v) in items]
            items.sort()
            items = [(k, v) for (v, k) in items]
        if sort_by == 'key':
            items.sort()
        for k, v in items:
            _model.append([str(k), v])
        cb.set_model(_model)
        cell = Gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 1)
        #cb.set_wrap_width(20)
        cb.set_active(0)


    def get_objects(self, *names):
        for name in names:
            widget = self.wTree.get_object(name)
            if widget is None:
                raise ValueError(_("Widget '%s' not found") % name)
            setattr(self, name, widget)


    def quit_application(self, *args):
        self.dialog.destroy()
        #only emit main_quit if we're running as a standalone app
        #todo do we need to do anyother clean-up here if we're _not_
        #running as a standalone app
        if self.exit_on_close:
            Gtk.main_quit
            sys.exit(0)


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print(_('Usage: voaAreaPlotgui file_to_plot.voa'))
        sys.exit(2)
    app = VOAAreaPlotGUI(sys.argv[-1])
    Gtk.main()
