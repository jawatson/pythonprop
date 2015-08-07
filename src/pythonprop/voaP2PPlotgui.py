#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voaP2PPlotgui.py
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
#import subprocess
import gettext
import locale

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

# todo restore the calls below
#Gtk.glade.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
#Gtk.glade.textdomain(GETTEXT_DOMAIN)
gettext.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
gettext.textdomain(GETTEXT_DOMAIN)


from voaOutFile import VOAOutFile
from voaP2PPlot import VOAP2PPlot
from voa3DPlot import VOA3DPlot

class VOAP2PPlotGUI:
    """GUI to create VOAArea Input Files"""
    
    # set the users itshfdata directory.  
    # todo mofify to suit windows as well...
    itshfbc_path = os.path.expanduser("~")+os.sep+'itshfbc' 


    plot_type_d = { 0: _('None'),
                    1: _('MUFday'),
                    2: _('Reliability'),
                    3: _('SNR'),
                    4: _('DBW')
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

 
    def __init__(self, data_source_filename, parent = None, exit_on_close = True,  datadir=""):
        self.datadir = datadir
        self.in_filename = data_source_filename
        #todo check the file exists
        in_file = VOAOutFile(self.in_filename)

        self.exit_on_close = exit_on_close
        #self.uifile = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voaP2PPlotgui.ui")
        self.parent = parent
        if self.parent:
            self.ui_file = os.path.join(self.datadir, "ui", "voaP2PPlotDialog.ui")
        else:
            self.ui_file = os.path.join(self.datadir, "ui", "voaP2PPlotWindow.ui")
        #self.wTree = Gtk.Builder.new_from_file(self.ui_file)

        self.wTree = Gtk.Builder()
        self.wTree.add_from_file(self.ui_file)

        self.get_objects("dialog", "type_combobox", "group_combobox", 
                                "tz_spinbutton", "cmap_combobox")
        if self.parent:
            self.dialog.set_transient_for(self.parent)
        
        self.dialog.set_title(_("Plot Control")) 

        if in_file.get_number_of_groups() >= 2:
            self.plot_type_d[5] = _('3D: MUF')

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

        d = { 0 : _('All Plots'),}
        l = in_file.get_group_titles()
        d.update(zip(range(1, len(l)+1), l))
        self.populate_combo(self.group_combobox, d, 'key')
                
        event_dic = { "on_dialog_destroy" : self.quit_application, 
                      "on_cancel_button_clicked" : self.quit_application,
                      "on_ok_button_clicked" : self.run_plot}
        self.wTree.connect_signals(event_dic)
        self.dialog.connect('delete_event', self.quit_application)
        if self.parent:
            self.dialog.run()
        else:
            self.dialog.show_all()
            Gtk.main()

    def run_plot(self, widget):
#        _color_map = self.cmap_list[self.cmap_combobox.get_active()]
#        _data_type = self.type_combobox.get_active()
        _color_map = self.cmap_combobox.get_model().get_value(self.cmap_combobox.get_active_iter(), 0)
        _data_type = int(self.type_combobox.get_model().get_value(self.type_combobox.get_active_iter(), 0))
        if self.group_combobox.get_active() == 0:
        	_plot_groups = ['a']
        else:
        	_plot_groups = [int(self.group_combobox.get_model().get_value(self.group_combobox.get_active_iter(),0))-1]
        _time_zone = self.tz_spinbutton.get_value_as_int()
        plot_parent = self.parent if self.parent else self.dialog
        if _data_type < 5:
            plot = VOAP2PPlot(self.in_filename,
                        data_type = _data_type,
                        plot_groups = _plot_groups,
                        time_zone = _time_zone,
                        color_map = _color_map,
                        parent = plot_parent)
        else: # do a 3D plot
            plot = VOA3DPlot(self.in_filename,
                        color_map = _color_map,
                        parent = plot_parent)
        #self.dialog.run()
        
 
    def populate_combo(self, cb, d, sort_by='value'):
        _model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING) 
        items = d.items()
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
                raise ValueError, _("Widget '%s' not found") % name
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
        print _('Usage: voaP2PPlotgui file_to_plot.out')
        sys.exit(2)
    app = VOAP2PPlotGUI(sys.argv[-1])
    Gtk.main()
