#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voacapgui
#
# Copyright (c) 2009-2013 J.Watson
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
import time
import re

import pkgutil
from . import templates

from dateutil.relativedelta import relativedelta
from calendar import monthrange

from configparser import *

from mpl_toolkits.basemap import Basemap
from mpl_toolkits.mplot3d import Axes3D

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GObject
    gi.require_version('GdkPixbuf', '2.0')
    from gi.repository import GdkPixbuf
    from gi.repository import Gtk
except ImportError as exc:
    print(("Error: failed to import gi module ({})".format(exc)))
    print ("Check that the python-gi module is installed")
    sys.exit(1)


import gettext
import locale
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
lang.install()


# glade file
# see http://bugzilla.gnome.org/show_bug.cgi?id=344926 for why the
# next two commands look repeated.
# TODO Restore the following 2 lines
#Gtk.Builder.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
#Gtk.Builder.textdomain(GETTEXT_DOMAIN)
gettext.bindtextdomain(GETTEXT_DOMAIN, LOCALE_PATH)
gettext.textdomain(GETTEXT_DOMAIN)


from .voaTextFileViewDialog import VOATextFileViewDialog
from .voaDatFile import *
from .voaDefaults import *
from .voaSiteChooser import *
from .voaP2PPlot import *
from .voaP2PPlotgui import *
from .voaAreaPlotgui import VOAAreaPlotGUI
from .ssnFetch import *
from .voaSSNThumb import *
from .voaFile import *
from .voaAreaChooser import *
from .voaAntennaChooser import *

class VOACAP_GUI():
    __gtype_name__ = 'PythonProp'

    """GUI to create VOAArea Input Files"""

    # Determine where the itshfbc and prefs files are, based on OS
    # The windows paths are guesses and need checking....
    if os.name == 'nt':
        itshfbc_path = 'C:\itshfbc'
        prefs_dir = 'C:\itshfbc\database\\'
    else:
        itshfbc_path = os.path.expanduser("~")+os.sep+'itshfbc'
        prefs_dir = os.path.expanduser("~")+os.sep+'.voacapgui'+os.sep


    prefs_path = prefs_dir + 'voacapgui.prefs'
    ssn_path = prefs_dir + 'ssn.json'
    # Check if the prefs directory exists, create one if if it doesn't
    # (This is probably not required as the installer will probably end up
    # creating and populating this directory.)

    if not os.path.isdir(prefs_dir):
        os.makedirs(prefs_dir)

    #ant_list = []

    firstCornerX = 0
    firstCornerY = 0

    area_rect = VOAAreaRect()

    model_list = ('CCIR', 'URSI88')
    path_list = (_('Short'), _('Long'))

    # These need to be lists later on to support multiple antennas
    tx_antenna_path = ''
    rx_antenna_path = ''

    main_window_size = (560, 410)
    site_chooser_map_size = area_chooser_map_size = (384,192)
    antenna_chooser_size = (500,400)

    def __init__(self, datadir="", pythonprop_version="dev"):
        self.datadir = datadir
        self.pythonprop_version = pythonprop_version
        self.area_templates_file = None
        #Set the GUI file
        #self.uifile = os.path.join(os.path.realpath(os.path.dirname(sys.argv[0])), "voacapgui.ui")
        self.ui_file = os.path.join(self.datadir, "ui", "voacapgui.ui")

        #self.builder = Gtk.Builder.new_from_file(self.ui_file)
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.ui_file)

        self.get_objects("main_window", "statusbar", "notebook",
                "tx_site_button", "tx_site_entry", "tx_lat_spinbutton",
                "tx_lon_spinbutton", "tx_antenna_button", "tx_antenna_entry",
                "tx_bearing_button", "tx_bearing_spinbutton",
                "tx_power_spinbutton", "rx_site_button", "rx_site_entry",
                "rx_lat_spinbutton", "rx_lon_spinbutton", "rx_antenna_button",
                "rx_antenna_entry", "rx_bearing_button",
                "rx_bearing_spinbutton", "ssn_tv", "ssn_plot_box",
                "ssn_file_data_label", "ssn_web_update_button",
                "foe_spinbutton", "fof1_spinbutton", "fof2_spinbutton",
                "foes_spinbutton", "model_combo", "path_combo",
                "mm_noise_spinbutton", "min_toa_spinbutton",
                "reliability_spinbutton", "snr_spinbutton", "mpath_spinbutton",
                "delay_spinbutton", "area_tv", "area_delbt", "area_clear_btn",
                "templatescb", "gridsizespinbutton", "add_templ_btn", "areayearspinbutton",
                "freqspinbutton", "monthspinbutton", "utcspinbutton", "add_templ_btn",
                "area_clear_btn", "area_select_btn", "area_label", "area_run_btn", "p2pmy_tv",
                "p2pfreq_tv", "p2pmydelbt", "p2pmyrstbt", "p2pfreqdelbt",
                "p2pfreqrstbt", "p2padd_mybt", "p2padd_freqbt",
                "p2pfreqspinbutton", "p2pdayspinbutton", "p2pmonthspinbutton",
                "p2pyearspinbutton", "p2pmethodcb", "p2prunbt",
                "p2pcircuitckb",
                "p2pcalbt", "p2pusedayck", "p2pmacrocb", "p2pmacroaddbt",
                )
        self.ssn_context_id = self.statusbar.get_context_id("SSN Messages")
        self.p2p_context_id = self.statusbar.get_context_id("P2P Messages")
        self.area_context_id = self.statusbar.get_context_id("Area Messages")

        # TODO clear up "p2psavebt", "p2pcircuitcb",
        self.p2p_useday = False
        self.p2pdayspinbutton.set_sensitive(self.p2p_useday)
        self.p2puseday_handler_id = self.p2pusedayck.connect('toggled', self.p2p_useday_tog)
        today = datetime.datetime.today()
        self.p2pyearspinbutton.set_value(today.year)
        self.p2pmonthspinbutton.set_value(today.month)
        self.p2pdayspinbutton.set_value(today.day)
        self.p2pfreqspinbutton.set_value(14.2)

        col_cm_t = [GObject.TYPE_UINT, GObject.TYPE_STRING]
        self.circuit_method_model = Gtk.ListStore(*col_cm_t)
        [ self.circuit_method_model.append([i, label]) for i, label in [
                (30, _("30: Smoothed LP/SP Model")),
                (25, _("25: All Modes SP Model")),
                (22, _("22: Forced SP Model")),
                (21, _("21: Forced LP Model")),
                (20, _("20: Complete System Performance")),
                (15, _("15: Tx. &amp; Rx. Antenna Pattern")),
                (14, _("14: Rx. Antenna Pattern")),
                (13, _("13: Tx. Antenna Pattern")),
                 (9, _("9: HPF-MUF-FOT Text Graph"))
                 ]]

        col_gm_t = [GObject.TYPE_UINT, GObject.TYPE_STRING]
        self.graphic_method_model = Gtk.ListStore(*col_gm_t)
        [ self.graphic_method_model.append([i, label]) for i, label in [
            (30, _("30: Smoothed LP/SP Model")),
            (22, _("22: Forced SP Model")),
            (21, _("21: Forced LP Model")),
            (20, _("20: Complete System Performance")) ]]


        self.main_window.resize(self.main_window_size[0], self.main_window_size[1])

        _model = Gtk.ListStore(GObject.TYPE_STRING)
        for item in self.model_list:
            _model.append([item])
        self.populate_combo(self.model_combo, _model)

        _model = Gtk.ListStore(GObject.TYPE_STRING)
        for item in self.path_list:
            _model.append([item])
        self.populate_combo(self.path_combo, _model)


        self.max_vg_files_warn = False
        self.max_frequencies_warn = False
        if os.name == 'posix':
            self.max_vg_files = 25 #This was originally set to 12 in earlier versions of voacapl.
        else:
            self.max_vg_files = 9 # DOS 8.3 filenames
        self.gridsizespinbutton.set_value(125)
        self.areayearspinbutton.set_value(today.year)
        self.monthspinbutton.set_value(today.month)
        self.freqspinbutton.set_value(14.1)
        self.p2pcircuitckb.set_active(False)
        self.set_circuit_panel_state(False)

        try:
            self.ssn_repo = SSNFetch(parent = self.main_window,
                save_location = self.ssn_path,
                s_bar=self.statusbar,
                s_bar_context=self.ssn_context_id)
        except NoSSNData as e:
            print((e.value))
            self.quit_application(None)
        _min, _max = self.ssn_repo.get_data_range()
        self.p2pyearspinbutton.set_range(_min.year, _max.year)
        self.areayearspinbutton.set_range(_min.year, _max.year)
        #self.write_ssns(self.ssn_repo.get_ssn_list())

        self.build_area_tv()
        self.ssn_build_tv()
        self.build_p2p_tvs()
        self.build_graphcb()
        self.build_macrocb()
        if os.path.isfile(self.prefs_path):
            self.read_user_prefs()

        if not self.area_templates_file:
            self.build_new_template_file()
        self.area_label.set_text(self.area_rect.get_formatted_string())
        self.build_area_template_ts()

        #Create event dictionary and connect it
        event_dic = { "on_main_window_destroy" : self.quit_application,
            "on_tx_site_button_clicked" : self.choose_site,
            "on_rx_site_button_clicked" : self.choose_site,
            "on_tx_antenna_button_clicked" : self.choose_antenna,
            "on_rx_antenna_button_clicked" : self.choose_antenna,
            "on_tx_antenna_entry_changed" : self.update_run_button_status,
            "on_rx_antenna_entry_changed" : self.update_run_button_status,
            "on_tx_bearing_button_clicked" : self.calculate_antenna_bearing,
            "on_rx_bearing_button_clicked" : self.calculate_antenna_bearing,
            #"on_mi_circuit_activate" : self.verify_input_data,
            #"on_mi_graph_activate" : self.verify_input_data,
            "on_mi_run_activate": self.run_prediction,
            "on_mi_show_yelp_activate": self.show_yelp,
            "on_mi_about_activate" : self.show_about_dialog,
            "on_mi_open_vgz_activate": self.open_vgz_file,
            "on_mi_quit_activate" : self.quit_application,
            "on_main_window_destroy" : self.quit_application,
            "on_ssn_web_update_button_clicked" : self.update_ssn_table,

            # notebook area page widgets event dict
            'on_notebook_switch_page' : self.nb_switch_page,
            'on_area_addbt_clicked' : self.area_add_tv_row_from_user,
            'on_add_templ_btn_clicked' : self.area_add_template,
            'on_templatescb_changed' : self.area_templatescb_change,
            'on_area_delbt_clicked' : self.area_del_tv_row,
            #'on_area_save_btn_clicked' : self.area_save_as_template,
            'on_area_clear_btn_clicked' : self.area_clean_tv,
            'on_area_select_btn_clicked' : self.show_area_chooser,
            'on_area_run_btn_clicked' : self.run_prediction,

            # notebook p2p page widgets event dict
            'on_p2pmonthspinbutton_value_changed' : self.p2p_set_days_range,
            'on_p2pyearspinbutton_value_changed' : self.p2p_set_days_range,
            'on_p2padd_mybt_clicked' : self.p2pmy_add_tv_row_from_user,
            'on_p2padd_freqbt_clicked' : self.p2pfreq_add_tv_row_from_user,
            'on_p2pmydelbt_clicked' : self.p2p_del_my_tv_row,
            'on_p2pfreqdelbt_clicked' : self.p2p_del_freq_tv_row,
            'on_p2psavebt_clicked' : self.p2p_save_as_template,
            'on_p2pmyrstbt_clicked' : self.p2p_clean_my_tv,
            'on_p2pfreqrstbt_clicked' : self.p2p_clean_freq_tv,
            'on_p2prunbt_clicked' : self.run_prediction,
            'on_p2pcalbt_clicked' : self.p2p_calendar,
#            'on_p2pusedayck_toggled' : self.p2p_useday_tog,
            'on_p2pmacroaddbt_clicked' : self.p2p_add_macro,
            'on_p2pcircuitckb_toggled' : self.p2p_toggle_circuit,
            'on_p2pmethodcb_changed' : self.p2p_method_changed
            }
        self.builder.connect_signals(event_dic)

        # area plot accelgrp
        self.area_accelgrp = None
        self.main_window.show_all()


        # test for ~/itshfbc tree
        if not os.path.exists(self.itshfbc_path):
            e = _("ITSHFBC directory not found")
            if os.name == 'posix':
                e_os = _("Please install voacap for Linux and run 'makeitshfbc'.\n")
            e_os += _("A 'itshfbc' directory cannot be found at: %s.\n") % (self.itshfbc_path)
            e_os += _("Please install voacap before running voacapgui.")
            dialog = Gtk.MessageDialog(self.main_window,
                Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, e )
            dialog.format_secondary_text(e_os)
            dialog.run()
            dialog.destroy()
            return -1


    def populate_combo(self, cb, model):
        cb.set_model(model)
        cell = Gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 0)
        #cb.set_wrap_width(20)
        cb.set_active(0)


    def p2p_set_days_range(self, widget):
        """
        Sets the adjustment of the 'days' spinbutton on the P2P panel, modifying the
        upper limit according to the values of the month/year.
        """
        current_day = self.p2pdayspinbutton.get_value()
        first_day, num_days = monthrange(int(self.p2pyearspinbutton.get_value()),\
                                         int(self.p2pmonthspinbutton.get_value()))
        adjustment = Gtk.Adjustment(1, 1, num_days, 1, 10, 0)
        if current_day > num_days: current_day = num_days
        self.p2pdayspinbutton.set_adjustment(adjustment)
        self.p2pdayspinbutton.set_value(current_day)


    def get_objects(self, *names):
        for name in names:
            widget = self.builder.get_object(name)
            if widget is None:
                raise ValueError("Widget '%s' not found" % name)
            setattr(self, name, widget)


    def choose_antenna(self, widget):
        dialog  = VOAAntennaChooser(self.itshfbc_path, size=self.antenna_chooser_size, parent=self.main_window, datadir=self.datadir)
        return_code, return_antenna, antenna_description, self.antenna_chooser_size = dialog.run()
        #print self.antenna_chooser_size
        if ((return_code == 0) and (return_antenna)): # response_id: 0=OK, 1=Cancel
            if widget == self.builder.get_object('tx_antenna_button'):
                self.tx_antenna_entry.set_text(return_antenna + ' : ' + antenna_description)
                self.tx_antenna_path = return_antenna
            else:
                self.rx_antenna_entry.set_text(return_antenna + ' : ' + antenna_description)
                self.rx_antenna_path = return_antenna


    def choose_site(self, widget):
        if widget == self.builder.get_object('tx_site_button'):
            lat = self.tx_lat_spinbutton.get_value()
            lon = self.tx_lon_spinbutton.get_value()
            name = self.tx_site_entry.get_text()
        elif widget == self.builder.get_object('rx_site_button'):
            lat = self.rx_lat_spinbutton.get_value()
            lon = self.rx_lon_spinbutton.get_value()
            name = self.rx_site_entry.get_text()
        else:
            lat = 0
            lon = 0
            name = ''

        dialog = VOASiteChooser(HamLocation(lat, lon, name), \
                            self.site_chooser_map_size, \
                            itshfbc_path=self.itshfbc_path, \
                            parent=self.main_window, \
                            datadir=self.datadir)
        return_code, location, self.site_chooser_map_size = dialog.run()
        if (return_code == 0): # response_id: 0=OK, 1=Cancel
            if widget == self.builder.get_object('tx_site_button'):
                self.tx_site_entry.set_text(location.get_name())
                self.tx_lat_spinbutton.set_value(location.get_latitude())
                self.tx_lon_spinbutton.set_value(location.get_longitude())
            else:
                self.rx_site_entry.set_text(location.get_name())
                self.rx_lat_spinbutton.set_value(location.get_latitude())
                self.rx_lon_spinbutton.set_value(location.get_longitude())


    def calculate_antenna_bearing(self, widget):
        try:
            tx_loc = HamLocation(self.tx_lat_spinbutton.get_value(),
                                        lon = self.tx_lon_spinbutton.get_value())
            rx_loc = HamLocation(float(self.rx_lat_spinbutton.get_value()),
                                        lon = self.rx_lon_spinbutton.get_value())
        except Exception:
            #todo add a note to the status bar explaining the reason
            #for the failure to actually do anything
            return
        if widget == self.builder.get_object('tx_bearing_button'):
            bearing, distance = tx_loc.path_to(rx_loc)
            self.tx_bearing_spinbutton.set_value(bearing)
        else:
            bearing, distance = rx_loc.path_to(tx_loc)
            self.rx_bearing_spinbutton.set_value(bearing)


    def read_user_prefs(self) :
        config = ConfigParser(VOADefaultDictionary())
        config.read(self.prefs_path)
        #set some defaults here for the system variables
        try:
            self.foe_spinbutton.set_value(float(config.get('DEFAULT','foe')))
            self.fof1_spinbutton.set_value(float(config.get('DEFAULT','fof1')))
            self.fof2_spinbutton.set_value(float(config.get('DEFAULT','fof2')))
            self.foes_spinbutton.set_value(float(config.get('DEFAULT','foes')))
            self.model_combo.set_active(int(config.get('DEFAULT', 'model')))
            self.path_combo.set_active(int(config.get('DEFAULT', 'path')))

            self.mm_noise_spinbutton.set_value(float(config.get('DEFAULT','mm_noise')))
            self.min_toa_spinbutton.set_value(float(config.get('DEFAULT','min_toa')))
            self.reliability_spinbutton.set_value(float(config.get('DEFAULT','required_reliability')))
            self.snr_spinbutton.set_value(float(config.get('DEFAULT','required_snr')))
            self.mpath_spinbutton.set_value(float(config.get('DEFAULT','mpath')))
            self.delay_spinbutton.set_value(float(config.get('DEFAULT','delay')))

            self.tx_bearing_spinbutton.set_value(float(config.get('DEFAULT', 'tx_bearing')))
            self.tx_power_spinbutton.set_value(float(config.get('DEFAULT', 'tx_power')))
            self.rx_bearing_spinbutton.set_value(float(config.get('DEFAULT', 'rx_bearing')))

            self.tx_site_entry.set_text(config.get('tx site','name'))
            self.tx_lat_spinbutton.set_value(float(config.get('tx site','lat')))
            self.tx_lon_spinbutton.set_value(float(config.get('tx site','lon')))
            self.tx_antenna_entry.set_text(config.get('tx site', 'antenna' ))
            self.tx_antenna_path, sep, suffix = (config.get('tx site', 'antenna' )).partition(' :')
            self.tx_bearing_spinbutton.set_value(float(config.get('tx site', 'bearing')))
            self.tx_power_spinbutton.set_value(float(config.get('tx site', 'power')))
            self.rx_site_entry.set_text(config.get('rx site','name'))
            self.rx_lat_spinbutton.set_value(float(config.get('rx site','lat')))
            self.rx_lon_spinbutton.set_value(float(config.get('rx site','lon')))
            self.rx_antenna_entry.set_text(config.get('rx site', 'antenna' ))
            self.rx_antenna_path, sep, suffix = (config.get('rx site', 'antenna' )).partition(' :')
            self.rx_bearing_spinbutton.set_value(float(config.get('rx site', 'bearing')))

            self.site_chooser_map_size = (config.getint('site chooser','map_width'),
                                          config.getint('site chooser','map_height'))
            self.area_chooser_map_size = (config.getint('area chooser','map_width'),
                                          config.getint('area chooser','map_height'))
            self.antenna_chooser_size = (config.getint('antenna chooser','width'),
                                          config.getint('antenna chooser','height'))
            self.gridsizespinbutton.set_value(config.getint('area', 'gridsize'))
            self.areayearspinbutton.set_value(config.getint('area','year'))
            self.monthspinbutton.set_value(config.getint('area','month'))
            self.utcspinbutton.set_value(config.getint('area','utc'))
            self.freqspinbutton.set_value(config.getfloat('area', 'frequency'))
            self.area_templates_file = config.get('area', 'templates_file')
            self.area_rect=VOAAreaRect(config.getfloat('area','sw_lat'),
                                        config.getfloat('area','sw_lon'),
                                        config.getfloat('area','ne_lat'),
                                        config.getfloat('area','ne_lon'))
            self.area_label.set_text(self.area_rect.get_formatted_string())
        except Exception as X:
            print('Error reading the user prefs: %s - %s' % (Exception, X))


    def save_user_prefs(self):
        config = ConfigParser()
        # voaSiteChooser map size
        config.add_section('site chooser')
        config.set('site chooser', 'map_width', str(self.site_chooser_map_size[0]))
        config.set('site chooser', 'map_height', str(self.site_chooser_map_size[1]))
        # voaAreaChooser map size
        config.add_section('area chooser')
        config.set('area chooser', 'map_width', str(self.area_chooser_map_size[0]))
        config.set('area chooser', 'map_height', str(self.area_chooser_map_size[1]))
        # voaAreaChooser map size
        if self.antenna_chooser_size:
            config.add_section('antenna chooser')
            config.set('antenna chooser', 'width', str(self.antenna_chooser_size[0]))
            config.set('antenna chooser', 'height', str(self.antenna_chooser_size[1]))
        # Tx Site Parameters
        config.add_section('tx site')
        config.set('tx site', 'name', self.tx_site_entry.get_text())
        config.set('tx site', 'lat', str(self.tx_lat_spinbutton.get_value()))
        config.set('tx site', 'lon', str(self.tx_lon_spinbutton.get_value()))
        config.set('tx site', 'antenna', self.tx_antenna_entry.get_text())
        config.set('tx site', 'bearing', str(self.tx_bearing_spinbutton.get_value()))
        config.set('tx site', 'power', str(self.tx_power_spinbutton.get_value()))
        # Rx Site Parameters
        config.add_section('rx site')
        config.set('rx site', 'name', self.rx_site_entry.get_text())
        config.set('rx site', 'lat', str(self.rx_lat_spinbutton.get_value()))
        config.set('rx site', 'lon', str(self.rx_lon_spinbutton.get_value()))
        config.set('rx site', 'antenna', self.rx_antenna_entry.get_text())
        config.set('rx site', 'bearing', str(self.rx_bearing_spinbutton.get_value()))
        # Ionospheric Parameters
        config.set('DEFAULT', 'foe', str(self.foe_spinbutton.get_value()))
        config.set('DEFAULT', 'fof1', str(self.fof1_spinbutton.get_value()))
        config.set('DEFAULT', 'fof2', str(self.fof2_spinbutton.get_value()))
        config.set('DEFAULT', 'foes', str(self.foes_spinbutton.get_value()))
        config.set('DEFAULT', 'model', str(self.model_combo.get_active()))
        config.set('DEFAULT', 'path', str(self.path_combo.get_active()))
        # System parameters
        config.set('DEFAULT','mm_noise', str(self.mm_noise_spinbutton.get_value()))
        config.set('DEFAULT','min_toa', str(self.min_toa_spinbutton.get_value()))
        config.set('DEFAULT','required_reliability', str(self.reliability_spinbutton.get_value()))
        config.set('DEFAULT','required_snr', str(self.snr_spinbutton.get_value()))
        config.set('DEFAULT','mpath', str(self.mpath_spinbutton.get_value()))
        config.set('DEFAULT','delay', str(self.delay_spinbutton.get_value()))
        # area parameters
        config.add_section('area')
        config.set('area','gridsize', str(self.gridsizespinbutton.get_value_as_int()))
        config.set('area','year', str(self.areayearspinbutton.get_value_as_int()))
        config.set('area','month', str(self.monthspinbutton.get_value_as_int()))
        config.set('area','utc', str(self.utcspinbutton.get_value_as_int()))
        config.set('area','frequency', str(self.freqspinbutton.get_value()))
        config.set('area','sw_lat', str(self.area_rect.sw_lat))
        config.set('area','sw_lon', str(self.area_rect.sw_lon))
        config.set('area','ne_lat', str(self.area_rect.ne_lat))
        config.set('area','ne_lon', str(self.area_rect.ne_lon))
        config.set('area','templates_file', self.area_templates_file if self.area_templates_file else '')

        with open(self.prefs_path, 'w') as configfile:
            config.write(configfile)


    def update_run_button_status(self, widget):
        """
        Called by elements that are common to both types of run
        """
        self.update_p2p_run_button_status()
        self.update_area_run_button_status()


    def update_p2p_run_button_status(self):
        """
        This method checks that the prerequistes for a P2P run are
        in place and enables the P2P run button accordingly.  It
        should be called everytime any of the prerequisites are modified.
        """
        valid = self.is_ssn_valid() and self.is_tx_site_data_valid() and self.is_rx_site_data_valid()
        if self.p2pcircuitckb.get_active():
            table_model = self.p2pfreq_tv.get_model()
            if (table_model):
                valid = valid and (len(table_model) > 0)
            else:
                valid = False
        table_model = self.p2pmy_tv.get_model()
        if (table_model):
            valid = valid and (len(table_model) > 0)
        else:
            valid = False

        iter = self.p2pmethodcb.get_active_iter()
        if self.p2pmethodcb.get_model().get_value(iter, 0) == 0:
            valid = False
        self.p2prunbt.set_sensitive(valid)


    def update_area_run_button_status(self):
        """
        This method checks that the prerequistes for an area run are
        in place and enables the area run button accordingly.  It
        should be called everytime any of the prerequiites are modified.
        """
        #def verify_input_data(self, widget):
        valid = self.is_ssn_valid() and self.is_tx_site_data_valid()

        table_model = self.area_tv.get_model()
        if (table_model):
            valid = valid and (len(table_model) > 0)
        else:
            valid = False

        self.area_run_btn.set_sensitive(valid)


    def is_ssn_valid(self):
        _valid = True
        _table_model = self.ssn_tv.get_model()
        if (_table_model):
            _valid = _valid and (len(_table_model) > 0)
        else:
            _valid = False

        if _valid != True:
            self.statusbar.push(self.ssn_context_id, _("No SSNs are defined"))
        return _valid


    def is_tx_site_data_valid(self):
        _is_valid = True
        if self.tx_power_spinbutton.get_value() == 0: _is_valid = False
        if self.tx_antenna_entry.get_text_length() == 0: _is_valid = False
        return _is_valid


    def is_rx_site_data_valid(self):
        _is_valid = True
        if self.rx_antenna_entry.get_text_length() == 0: _is_valid = False
        return _is_valid

#gettext here
#This function is used to force an update
    def update_ssn_table(self, widget):
        self.ssn_repo.update_ssn_file() #Force an update
#        self.update_ssn_data_label()
        self.ssn_file_data_label.set_text(self.ssn_repo.get_file_data())
        #self.write_ssns(self.ssn_repo.get_ssn_list())
        self.scroll_ssn_tv_to_current_year()


    def scroll_ssn_tv_to_current_year(self):
        # scroll to the current year
        iter = self.ssn_repo.get_iter_first()
        while iter:
            if self.ssn_repo.get_value(iter, self.ssn_tv_idx_year) == str(datetime.datetime.today().year):
                path = self.ssn_repo.get_path(iter)
                self.ssn_tv.set_cursor(path)
                self.ssn_tv.scroll_to_cell(path, None)
                break
            iter = self.ssn_repo.iter_next(iter)


    def update_ssn_data_label(self):
        _text = _("SSN Data Last Updated:\n")
        _text += self.ssn_repo.get_file_mtime_str()
        self.ssn_file_data_label.set_text(_text)


    def p2p_toggle_circuit(self, widget):
        self.set_circuit_panel_state(widget.get_active())
        self.update_p2p_run_button_status()


    def set_circuit_panel_state(self, state):
        self.p2pfreqspinbutton.set_sensitive(state)
        self.p2padd_freqbt.set_sensitive(state)
        self.p2pfreqdelbt.set_sensitive(state)
        self.p2pfreqrstbt.set_sensitive(state)
        self.p2pfreq_tv.set_sensitive(state)
        self.build_graphcb()


    def p2p_method_changed(self, widget):
        self.update_p2p_run_button_status()


    def build_p2p_tvs(self):
       # grey out delete and save buttons, since there are no entries in the model
        self.p2pmydelbt.set_sensitive(False)
        self.p2pmyrstbt.set_sensitive(False)
        self.p2pfreqdelbt.set_sensitive(False)
        self.p2pfreqrstbt.set_sensitive(False)
        self.p2prunbt.set_sensitive(False)
        # model:  day, month name, month_ordinal, year
        col_t = [ GObject.TYPE_UINT,
                  GObject.TYPE_STRING, GObject.TYPE_UINT, GObject.TYPE_UINT]
        model_my = Gtk.ListStore(*col_t)

        col_t = [GObject.TYPE_STRING]
        model_freq = Gtk.ListStore(*col_t)

        self.p2pmy_tv.set_model(model_my)
        self.p2pfreq_tv.set_model(model_freq)

        self.p2pmy_tv.set_property("rules_hint", True)
        self.p2pmy_tv.set_property("enable_search", False)
        self.p2pmy_tv.set_headers_visible(True)
        self.p2pmy_tv.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        self.p2pfreq_tv.set_property("rules_hint", True)
        self.p2pfreq_tv.set_property("enable_search", False)
        self.p2pfreq_tv.set_headers_visible(True)
        self.p2pfreq_tv.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        # col idx
        self.p2pmy_tv_idx_day = 0
        self.p2pmy_tv_idx_month_n = 1
        self.p2pmy_tv_idx_month_i = 2
        self.p2pmy_tv_idx_year = 3

        self.p2pfreq_tv_idx_freq = 0

        def dow_celldatafunction(column, cell, model, iter, user_data=None):
           t = ''
           d = model.get_value(iter, self.p2pmy_tv_idx_day)
           m = model.get_value(iter, self.p2pmy_tv_idx_month_i)
           y = model.get_value(iter, self.p2pmy_tv_idx_year)
           if d: t = datetime.datetime(y,m,d).strftime('%d')
           cell.set_property('text', t)

        title = _("Day")
        cell = Gtk.CellRendererText()
        tvcol = Gtk.TreeViewColumn(title, cell)
#        tvcol.add_attribute(cell, 'text' , self.p2pmy_tv_idx_month_n)
#        tvcol.set_sort_column_id(self.p2pmy_tv_idx_month_n)
        tvcol.set_cell_data_func(cell, dow_celldatafunction)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        self.p2pmy_tv.append_column(tvcol)

        title = _("Month")
        cell = Gtk.CellRendererText()
        tvcol = Gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.p2pmy_tv_idx_month_n)
        tvcol.set_sort_column_id(self.p2pmy_tv_idx_month_n)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        self.p2pmy_tv.append_column(tvcol)

        title = _("Year")
        cell = Gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = Gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.p2pmy_tv_idx_year)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.p2pmy_tv_idx_year)
        self.p2pmy_tv.append_column(tvcol)

        title = _("Frequency (MHz)")
        cell = Gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = Gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.p2pfreq_tv_idx_freq)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.p2pfreq_tv_idx_freq)
        self.p2pfreq_tv.append_column(tvcol)


    def build_graphcb(self):
        if self.p2pcircuitckb.get_active():
            model = self.circuit_method_model
        else:
            model = self.graphic_method_model

        self.p2pmethodcb.clear()
        self.p2pmethodcb.set_model(model)
        cell = Gtk.CellRendererText()
        self.p2pmethodcb.pack_start(cell, True)
        self.p2pmethodcb.add_attribute(cell, 'text', 1)
        self.p2pmethodcb.set_active(0)



    def build_macrocb(self):
        col_t = [GObject.TYPE_STRING, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT]
        model = Gtk.ListStore(*col_t)
        [ model.append([l,f,a]) for l,f,a in [
            (_("Select set to load"), None, None),
            (_("Next 3 months"), self.p2p_macro_next_months, [3]),
            (_("Next 6 months"), self.p2p_macro_next_months, [6]),
            (_("Next 12 months"), self.p2p_macro_next_months, [12]),
            (_("Next 24 months"), self.p2p_macro_next_months, [24]),
            (_("Next 30 days"), self.p2p_macro_next_days, [30]),
            (_("Annual (Quarters)"), self.p2p_macro_annual, [4]),
            (_("Annual (bi-month)"), self.p2p_macro_annual, [6]),
            ]]
        self.p2pmacrocb.set_model(model)
        cell = Gtk.CellRendererText()
        self.p2pmacrocb.pack_start(cell, True)
        self.p2pmacrocb.add_attribute(cell, 'text', 0)
        self.p2pmacrocb.set_active(0)


    def p2p_macro_next_months(self, vals):
        day = 0

        # if the tv has any entries, use the last one as our
        # start in the sequence.
        tv_model = self.p2pmy_tv.get_model()
        tv_iter = tv_model.get_iter_first()
        if tv_iter == None:
            #empty model
            #so let's add this month to the model
            today = date.today()
            self.p2pmy_add_tv_rows([(day, today.month, today.year)])
        else:
            # the table has entries.  find the last entry and use that
            # as our starting point for the 'next' months
            last_iter = None
            while tv_iter:
                last_iter = tv_iter
                tv_iter = tv_model.iter_next(tv_iter)
            month = tv_model.get_value(last_iter, self.p2pmy_tv_idx_month_i)
            year = tv_model.get_value(last_iter, self.p2pmy_tv_idx_year)
            today = date(year, month, 1)
            #get the last entry
            #build the value for today


        mr = relativedelta(months=+1)
        if len(vals) == 1:
            next = today + mr
            for n in range(vals[0]):
                self.p2pmy_add_tv_rows([(day, next.month, next.year)])
                next = next + mr
        elif len(vals) >1:
            pass

    def p2p_macro_next_days(self, vals):
        if not self.p2p_useday:
            self.p2pusedayck.set_active(True)
        today = date.today()
        dr = relativedelta(days=+1)
        if len(vals) == 1:
            next = today + dr
            for n in range(vals[0]):
                self.p2pmy_add_tv_rows([(next.day, next.month, next.year)])
                next = next + dr
        elif len(vals) >1:
            pass

    def p2p_macro_annual(self, vals):
        day = 0
        # start the count from Jan of the current year
        year = self.p2pyearspinbutton.get_value_as_int()
        today = date(year, 1, 1)
        self.p2pmy_add_tv_rows([(day, today.month, today.year)])
        mr = relativedelta(months=+(12/vals[0]))
        if len(vals) == 1:
            next = today + mr
            for n in range(vals[0]-1):
                self.p2pmy_add_tv_rows([(day, next.month, next.year)])
                next = next + mr
        elif len(vals) >1:
            pass

    def p2p_macro_next_days(self, vals):
        if not self.p2p_useday:
            self.p2pusedayck.set_active(True)
        today = date.today()
        dr = relativedelta(days=+1)
        if len(vals) == 1:
            next = today + dr
            for n in range(vals[0]):
                self.p2pmy_add_tv_rows([(next.day, next.month, next.year)])
                next = next + dr
        elif len(vals) >1:
            pass

    def p2p_add_macro(self, *args):
        model = self.p2pmacrocb.get_model()
        f, args = model.get(self.p2pmacrocb.get_active_iter(),1,2)
        if not f: return
        f(args)


    def build_area_tv(self):
        # grey out delete and save buttons, since there are no entries in the model
        self.area_delbt.set_sensitive(False)
        self.area_clear_btn.set_sensitive(False)
        #self.area_save_btn.set_sensitive(False)
        self.area_run_btn.set_sensitive(False)
        # model: year, month name, month_ordinal, utc time hour, freq in Hz
        col_t = [GObject.TYPE_UINT, GObject.TYPE_STRING, GObject.TYPE_UINT, GObject.TYPE_UINT, GObject.TYPE_STRING]
        model = Gtk.ListStore(*col_t)
        self.area_tv.set_model(model)
        self.area_tv.set_property("rules_hint", True)
        self.area_tv.set_property("enable_search", False)
        self.area_tv.set_headers_visible(True)
        self.area_tv.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        # col idx
        self.area_tv_idx_year = 0
        self.area_tv_idx_month_n = 1
        self.area_tv_idx_month_i = 2
        self.area_tv_idx_utc = 3
        self.area_tv_idx_freq = 4

        title = _("Year")
        cell = Gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = Gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.area_tv_idx_year)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.area_tv_idx_year)
        self.area_tv.append_column(tvcol)

        title = _("Month")
        cell = Gtk.CellRendererText()
        tvcol = Gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.area_tv_idx_month_n)
        tvcol.set_sort_column_id(self.area_tv_idx_month_n)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        self.area_tv.append_column(tvcol)

        title = _("Time (UTC)")
        cell = Gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = Gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.area_tv_idx_utc)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.area_tv_idx_utc)
        self.area_tv.append_column(tvcol)

        title = _("Frequency (MHz)")
        cell = Gtk.CellRendererText()
        cell.set_property('xalign', 1.0)
        tvcol = Gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text' , self.area_tv_idx_freq)
        tvcol.set_resizable(True)
        tvcol.set_reorderable(True)
        tvcol.set_sort_column_id(self.area_tv_idx_freq)
        self.area_tv.append_column(tvcol)

    def build_area_template_ts(self):
        # loads templates from a file and populates the combobox
        model = self.templatescb.get_model()
        if not model:
            col_t =  [GObject.TYPE_STRING, GObject.TYPE_PYOBJECT] # name, (year,month,utc,freq)
            model = Gtk.ListStore(*col_t)
            self.templatescb.set_model(model)
            cell = Gtk.CellRendererText()
            self.templatescb.pack_start(cell, True)
            self.templatescb.add_attribute(cell, 'text', 0)
        model.clear()

        # this hack for letting the templates subdir be parth of the path
        # so the templates/*.py can import between themselves
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(os.path.join(current_dir, 'templates'))

        # Revised module loading thanks to the following link
        # http://stackoverflow.com/questions/3365740/how-to-import-all-submodules
        for loader, module_name, is_pkg in  pkgutil.walk_packages(templates.__path__):
            try:
                t_o = loader.find_module(module_name).load_module(module_name).templates(self.main_window)
            except Exception as X:
                print((" Failed to import module %s %s ") % (module_name, X))
                continue

            # set module parameters
            ps = t_o.get_params()
            for p in ps:
                try:
                    t_o.__dict__[p] = self.__dict__[p]
                except Exception as X:
                    print(_("Fail to set property %s in template %s: %s") % (p, f, X))
            # make the module get ready for use later
            ret = t_o.load()
            if ret:
                print(_("Can't load() template module %s") % f)
                continue

            for tname in t_o.get_names():
                model.append([tname, t_o])

        if not len(model):
            # put an informative entry in the model
            model.append([_('There are no templates available'), None])
        else:
            model.prepend([_('Select a template to load'), None])
        self.templatescb.set_active(0)
        self.add_templ_btn.set_sensitive(False)


    def area_templatescb_change(self, *args):
        active = self.templatescb.get_active()
        if not active:# 0 is the indicative default, not a real template
            self.add_templ_btn.set_sensitive(False)
        else:
            self.add_templ_btn.set_sensitive(True)


    def p2p_useday_tog(self, *args):
        change_to = None
        e = ee = ''
        #we only need to display a warning if the coeffs change.
        if self.p2pusedayck.get_active():
            e = _("URSI88 coefficients")
            ee = _("Specifying days forces the use of URSI88 coefficients. ")
            if len(self.p2pmy_tv.get_model()):
                ee += _("Values of 'day' in existing entries will be set to '1'.")
                change_to = 1
        else:
            e = _("Not specifing days reverts the forced use of URSI88 coefficients. \
The current setting is %s.") % ('CCIR' if (self.model_combo.get_active()==0) else 'URSI88')
            if len(self.p2pmy_tv.get_model()):
                ee = _("All existing day values will be deleted.")
                change_to = 0
        dialog = Gtk.MessageDialog(self.main_window,
                Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, e)
        dialog.set_title(_('Warning'))
        dialog.format_secondary_text(ee)
        ret = dialog.run()
        dialog.destroy()
        if ret != -5:
            self.p2pusedayck.handler_block(self.p2puseday_handler_id)
            if self.p2pusedayck.get_active():
                self.p2pusedayck.set_active(False)
            else:
                self.p2pusedayck.set_active(True)
            self.p2pusedayck.handler_unblock(self.p2puseday_handler_id)
            return

        self.p2p_useday = self.p2pusedayck.get_active()
        if self.p2p_useday:
            self.model_combo.set_active(1)
            self.model_combo.set_sensitive(False)
        else:
            self.model_combo.set_sensitive(True)

        self.p2pdayspinbutton.set_sensitive(self.p2p_useday)
        model = self.p2pmy_tv.get_model()
        iter = model.get_iter_first()
        while iter:
            model.set_value(iter, self.p2pmy_tv_idx_day, change_to)
            iter = model.iter_next(iter)


    def p2p_calendar(self, *args):
        def calendar_retval(cal, dialog):
            dialog.response(Gtk.ResponseType.ACCEPT)
        dialog = Gtk.Dialog(_("Select date"), self.main_window,
                              Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.WindowPosition.CENTER_ON_PARENT,
                              (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                              Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        cal = Gtk.Calendar()
        cal.connect('day-selected-double-click', calendar_retval, dialog)
        dialog.vbox.pack_start(cal, True, True, 0)
        dialog.show_all()
        # set def date as the last date used, else let it default to today
        try:
            cal.select_month(self.p2pcal_last[1], self.p2pcal_last[0])
            cal.select_day(self.p2pcal_last[2])
        except:
            pass
        ret = dialog.run()
        dialog.destroy()
        if ret != -3: #ok
            return
        self.p2pcal_last = cal.get_date()
        self.p2pmy_add_tv_rows([(self.p2pcal_last[2], self.p2pcal_last[1]+1, self.p2pcal_last[0])])

    def p2pmy_add_tv_row_from_user(self, *args):
        day = self.p2pdayspinbutton.get_value_as_int()
        month_i = self.p2pmonthspinbutton.get_value_as_int()
        year = self.p2pyearspinbutton.get_value_as_int()
        self.p2pmy_add_tv_rows([(day, month_i, year)])

    def p2pfreq_add_tv_row_from_user(self, *args):
        freq = self.p2pfreqspinbutton.get_value()
        self.p2pfreq_add_tv_rows([(freq)])

    def p2pmy_add_tv_rows(self, rows):
        # rows: a list of (day, month_i, year) tuples
        tv_model = self.p2pmy_tv.get_model()
        had_rows = len(tv_model)
        for (day, month_i, year) in rows:
            day = day if self.p2p_useday else 0
            month_n = time.strftime('%B', time.strptime(str(month_i), '%m'))
            row = []
            row.insert(self.p2pmy_tv_idx_day, day)
            row.insert(self.p2pmy_tv_idx_month_n, month_n)
            row.insert(self.p2pmy_tv_idx_month_i, month_i)
            row.insert(self.p2pmy_tv_idx_year, year)
            iter = tv_model.append(row)
        self.p2pmydelbt.set_sensitive(True)
        self.p2pmyrstbt.set_sensitive(True)
        self.update_p2p_run_button_status()
#       if self.area_templates_file:
#           self.p2psavebt.set_sensitive(True)
#        self.verify_input_data(None)
        # def focus first row if the tv was previously empty
        if not had_rows:
            self.p2pmy_tv.set_cursor(0)

    def p2pfreq_add_tv_rows(self, rows):
        # rows: a list of (freq) tuples
        tv_model = self.p2pfreq_tv.get_model()
        had_rows = len(tv_model)
        for (freq) in rows:
            row = []
            row.insert(self.p2pfreq_tv_idx_freq, '%.3f' % freq)
            iter = tv_model.append(row)
        self.p2pfreqdelbt.set_sensitive(True)
        self.p2pfreqrstbt.set_sensitive(True)
        self.update_p2p_run_button_status()
        if not had_rows:
            self.p2pfreq_tv.set_cursor(0)
        if len(tv_model) > 11 and not self.max_frequencies_warn:
            e = _("VOACAP can only process 11 frequencies")
            dialog = Gtk.MessageDialog(self.main_window,
                    Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, e)
            dialog.format_secondary_text(_('Only the first 11 entries will \
be processed, all other entries will be ignored.  Please delete some entries \
from the frequency table.'))
            dialog.run()
            dialog.destroy()
            self.max_frequencies_warn = True

    def area_add_tv_row_from_user(self, *args):
        year = self.areayearspinbutton.get_value_as_int()
        month_i = self.monthspinbutton.get_value_as_int()
        utc = self.utcspinbutton.get_value_as_int()
        freq = self.freqspinbutton.get_value()
        self.area_add_tv_rows([(year, month_i, utc, freq)])

    def area_add_tv_rows(self, rows):#month_i, utc, freq, model=self.area_tv.get_model()):
        # rows: a list of (month_i, utc, freq) tuples
        tv_model = self.area_tv.get_model()
        had_rows = len(tv_model)
        for (year, month_i, utc, freq) in rows:
            month_n = time.strftime('%B', time.strptime(str(month_i), '%m'))
            row = []
            row.insert(self.area_tv_idx_year, year)
            row.insert(self.area_tv_idx_month_n, month_n)
            row.insert(self.area_tv_idx_month_i, month_i)
            row.insert(self.area_tv_idx_utc, utc)
            row.insert(self.area_tv_idx_freq, '%.3f' % freq)
            iter = tv_model.append(row)

        self.area_delbt.set_sensitive(True)
        self.area_clear_btn.set_sensitive(True)
        self.update_area_run_button_status()
        # def focus first row if the tv was previously empty
        if not had_rows:
            self.area_tv.set_cursor(0)
        #let the user know we did not run all their data
        if len(tv_model) > self.max_vg_files and not self.max_vg_files_warn:
            e = _("VOACAP can only process %d area entries") % self.max_vg_files
            dialog = Gtk.MessageDialog(self.main_window,
                    Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, e)
            dialog.format_secondary_text(_('Only the first 12 entries will \
be processed, all other entries will be ignored.  Please delete some entries.'))
            dialog.run()
            dialog.destroy()
            self.max_vg_files_warn = True

    def p2p_clean_my_tv(self, *args):
        self.p2pmy_tv.get_model().clear()
        self.p2pmydelbt.set_sensitive(False)
        self.p2pmyrstbt.set_sensitive(False)
        self.update_p2p_run_button_status()

    def p2p_clean_freq_tv(self, *args):
        self.p2pfreq_tv.get_model().clear()
        self.p2pfreqdelbt.set_sensitive(False)
        self.p2pfreqrstbt.set_sensitive(False)
        self.update_p2p_run_button_status()

    def area_clean_tv(self, *args):
        self.area_tv.get_model().clear()
        self.area_delbt.set_sensitive(False)
        self.area_clear_btn.set_sensitive(False)
        self.area_run_btn.set_sensitive(False)
        #self.update_p2p_run_button_status()

    def p2p_del_my_tv_row(self, *args):
        selection = self.p2pmy_tv.get_selection()
        if not selection.count_selected_rows(): return
        model, paths = selection.get_selected_rows()
        self.p2pmy_tv.freeze_child_notify()
        self.p2pmy_tv.set_model(None)
        iters = []
        for path in paths:
            iters.append(model.get_iter(path))
        for iter in iters:
            model.remove(iter)
        if not len(model):
            self.p2pmydelbt.set_sensitive(False)
            self.p2pmyrstbt.set_sensitive(False)
            self.update_p2p_run_button_status()
        self.p2pmy_tv.set_model(model)
        self.p2pmy_tv.thaw_child_notify()
        # select next row if it's there, or the previous instead
        last_path = paths[-1][0]+1
        for i in range(len(model) +1):
            last_path -= 1
            try:
                model.get_iter(last_path)
            except:
                pass
            else:
                self.p2pmy_tv.set_cursor((last_path,))
                return

    def p2p_del_freq_tv_row(self, *args):
        selection = self.p2pfreq_tv.get_selection()
        if not selection.count_selected_rows(): return
        model, paths = selection.get_selected_rows()
        self.p2pfreq_tv.freeze_child_notify()
        self.p2pfreq_tv.set_model(None)
        iters = []
        for path in paths:
            iters.append(model.get_iter(path))
        for iter in iters:
            model.remove(iter)
        if not len(model):
            self.p2pfreqdelbt.set_sensitive(False)
            self.p2pfreqrstbt.set_sensitive(False)
            self.update_p2p_run_button_status()
        self.p2pfreq_tv.set_model(model)
        self.p2pfreq_tv.thaw_child_notify()
        # select next row if it's there, or the previous instead
        last_path = paths[-1][0]+1
        for i in range(len(model) +1):
            last_path -= 1
            try:
                model.get_iter(last_path)
            except:
                pass
            else:
                self.p2pfreq_tv.set_cursor((last_path,))
                return


    def area_del_tv_row(self, *args):
        selection = self.area_tv.get_selection()
        if not selection.count_selected_rows(): return
        model, paths = selection.get_selected_rows()
        self.area_tv.freeze_child_notify()
        self.area_tv.set_model(None)
        iters = []
        for path in paths:
            iters.append(model.get_iter(path))
        for iter in iters:
            model.remove(iter)
        if not len(model):
            self.area_delbt.set_sensitive(False)
            self.area_clear_btn.set_sensitive(False)
            self.update_area_run_button_status()
        self.area_tv.set_model(model)
        self.area_tv.thaw_child_notify()
        # select next row if it's there, or the previous instead
        last_path = paths[-1][0]+1
        for i in range(len(model) +1):
            last_path -= 1
            try:
                model.get_iter(last_path)
            except:
                pass
            else:
                self.area_tv.set_cursor((last_path,))
                return


    def p2p_save_as_template(self, *args):
        pass


    def area_save_as_template(self, *args):
        ''' saves area_tv model content as a template '''
        global ok_bt
        global nentry

        def text_change(self, *args):
            global ok_bt
            global nentry
            if len(nentry.get_text()):
                ok_bt.set_sensitive(True)
            else:
                ok_bt.set_sensitive(False)

        dialog = Gtk.Dialog(_("Creating new area template"),
                   self.main_window,
                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT))
        hb = Gtk.HBox(2)
        label = Gtk.Label(label=_("Template name"))
        hb.pack_start(label, True, True, 0)
        nentry = Gtk.Entry(max=50)
        nentry.connect("changed", text_change)
        hb.pack_start(nentry, True, True, 0)
        hb.show_all()
        dialog.vbox.pack_start(hb, True, True, 0)

        ok_bt = Gtk.Button(None, Gtk.STOCK_OK)
        ok_bt.set_sensitive(False)
        ok_bt.show()
        dialog.add_action_widget(ok_bt, Gtk.ResponseType.ACCEPT)

        response = dialog.run()
        if response == -3: # accept
            # save it
            fd = open(os.path.expandvars(self.area_templates_file), 'a')
            fd.write(_('\n#template created by voacap GUI'))
            title = nentry.get_text()
            fd.write('\n[%s]' % title)
            fd.write(_('\n#month utchour  freq'))
            model = self.area_tv.get_model()
            iter = model.get_iter_first()
            while iter:
                m,u,f = model.get(iter,1,2,3)
                fd.write('\n%02d      %02d      %.3f' % (m,u,float(f)))
                iter = model.iter_next(iter)
            fd.write(_('\n#End of %s') % title)
            fd.close()
            # reload templates_file to repopulate templatescb, then
            # select this recently saved as the active one
            self.build_area_template_ts()
            model = self.templatescb.get_model()
            iter = model.get_iter_first()
            while iter:
                if model.get_value(iter, 0) == title:
                    self.templatescb.set_active_iter(iter)
                    break
                iter = model.iter_next(iter)
        dialog.destroy()


    def area_add_template(self, *args):
        active = self.templatescb.get_active()
        if not active:# 0 is the indicative default, not a real template
            return
        model = self.templatescb.get_model()
        t_n = model.get_value(model.get_iter(active), 0)
        t_o = model.get_value(model.get_iter(active), 1)
        model = self.area_tv.get_model()
        if t_o.set_ini(model):
            print("Can't initialize module %s" % t_n)
            return
        if t_o.run(): return
        try:
            templ_tups = t_o.ret_templates[t_n]
        except: pass
        if templ_tups:
            self.area_add_tv_rows(templ_tups)




#####################SSN Tab functions follow
    def ssn_build_tv(self):
        self.ssn_tv.set_model(self.ssn_repo)

        self.ssn_file_data_label.set_text(self.ssn_repo.get_file_data())

        self.ssn_tv.set_property("rules_hint", True)
        self.ssn_tv.set_property("enable_search", False)
        self.ssn_tv.set_headers_visible(True)

        # col idx
        self.ssn_tv_idx_year = 0

        title = _("Year")
        cell = Gtk.CellRendererText()
        font = Pango.FontDescription('bold')
        cell.set_property('font-desc', font)
        tvcol = Gtk.TreeViewColumn(title, cell)
        tvcol.add_attribute(cell, 'text', self.ssn_tv_idx_year)
        tvcol.set_sort_column_id(self.area_tv_idx_month_n)
        tvcol.set_resizable(True)
        tvcol.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        tvcol.set_expand(True)
        self.ssn_tv.append_column(tvcol)

        for i in range (1,13):
            cell = Gtk.CellRendererText()
            cell.set_property('xalign', 0.5)
            tvcol = Gtk.TreeViewColumn(calendar.month_abbr[i], cell)
            tvcol.set_alignment(0.5)
            tvcol.add_attribute(cell, 'text', i)
            #tvcol.add_attribute(cell, 'font', i+13)
            tvcol.set_resizable(True)
            tvcol.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            tvcol.set_expand(True)
            self.ssn_tv.append_column(tvcol)

        ssn_thumb = VOASSNThumb(self.ssn_repo)
        _th = ssn_thumb.get_thumb()
        _th.show()
        self.ssn_plot_box.pack_start(_th, True, True, 0)
        self.scroll_ssn_tv_to_current_year()


    def nb_switch_page(self, *args):
        # area is the last page in the nb
        if self.notebook.get_n_pages() == args[2] +1:
            if not self.area_accelgrp:
                self.area_accelgrp = Gtk.AccelGroup()
                self.area_accelgrp.connect(0xffff, 0, 0, self.area_del_tv_row)
            self.main_window.add_accel_group(self.area_accelgrp)
        else:
            if self.area_accelgrp:
                self.main_window.remove_accel_group(self.area_accelgrp)
                self.area_accelgrp = None


    def show_area_chooser(self, widget):
        dialog = VOAAreaChooser(self.area_rect, self.area_chooser_map_size, parent=self.main_window, datadir=self.datadir)
        return_code, return_rect, return_size = dialog.run()
        if (return_code == 0): # 0=ok, 1=cancel
            self.area_rect = return_rect
            self.area_chooser_map_size = return_size
            self.area_label.set_text(self.area_rect.get_formatted_string())


    def run_prediction(self, button):
        voacapl_args = ''

        if button == self.area_run_btn:
            voacapl_args = self.itshfbc_path
            ###################################################################
            vf = VOAFile(os.path.join(os.path.expanduser("~"),'itshfbc','areadata','pyArea.voa'))
            vf.set_gridsize(self.gridsizespinbutton.get_value())
            vf.set_location(vf.TX_SITE,
                            self.tx_site_entry.get_text(),
                            self.tx_lon_spinbutton.get_value(),
                            self.tx_lat_spinbutton.get_value())
            vf.P_CENTRE = vf.TX_SITE

            vf.set_xnoise(self.mm_noise_spinbutton.get_value())
            vf.set_amind(self.min_toa_spinbutton.get_value())
            vf.set_xlufp(self.reliability_spinbutton.get_value())
            vf.set_rsn(self.snr_spinbutton.get_value())
            vf.set_pmp(self.mpath_spinbutton.get_value())
            vf.set_dmpx(self.delay_spinbutton.get_value())

            vf.set_psc1(self.foe_spinbutton.get_value())
            vf.set_psc2(self.fof1_spinbutton.get_value())
            vf.set_psc3(self.fof2_spinbutton.get_value())
            vf.set_psc4(self.foes_spinbutton.get_value())

            vf.set_area(self.area_rect)

            # Antennas, gain, tx power, bearing
            #def set_rx_antenna(self, data_file, gain=0.0, bearing=0.0):
            #rel_dir, file, description = self.ant_list[self.rx_ant_combobox.get_active()]
            vf.set_rx_antenna(self.rx_antenna_path.ljust(21), 0.0,
                self.rx_bearing_spinbutton.get_value())

            #def set_tx_antenna(self, data_file, design_freq=0.0, bearing=0.0, power=0.125):
            #rel_dir, file, description = self.ant_list[self.tx_ant_combobox.get_active()]
            vf.set_tx_antenna(self.tx_antenna_path.ljust(21), 0.0,
                self.tx_bearing_spinbutton.get_value(),
                self.tx_power_spinbutton.get_value()/1000.0)

            vf.clear_plot_data()
            # treeview params
            model = self.area_tv.get_model()
            iter = model.get_iter_first()
            # we're limited to 12 entries here
            i = 0
            while iter and i < self.max_vg_files:
                year = int(model.get_value(iter, self.area_tv_idx_year))
                month_i = float(model.get_value(iter, self.area_tv_idx_month_i))
                utc = model.get_value(iter, self.area_tv_idx_utc)
                freq = model.get_value(iter, self.area_tv_idx_freq)
                # ssn entries are named as months (jan_ssn_entry) so to be sure
                # we're getting the correct one, we need to map them
                ssn = self.ssn_repo.get_ssn(str(int(month_i)), year)
                vf.add_plot((freq, utc, month_i, ssn))
                iter = model.iter_next(iter)
                i = i+1
            vf.write_file()
            #let the user know we did not run all their data
            if iter:
                e = _("VOACAP can only process %d area entries") % self.max_vg_files
                dialog = Gtk.MessageDialog(self.main_window,
                    Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, e)
                dialog.format_secondary_text(_('Only the first 12 entries will be processed,\
all other entries will be ignored.'))
                dialog.run()
                dialog.destroy()

            self.statusbar.pop(self.area_context_id)
            self.statusbar.push(self.area_context_id, "Running prediction...")
            while Gtk.events_pending():
                Gtk.main_iteration()
            ret = os.spawnlp(os.P_WAIT, 'voacapl', 'voacapl', os.path.join(os.path.expanduser("~"), 'itshfbc'), "area", "calc",  "pyArea.voa")

            if ret:
                self.statusbar.pop(self.area_context_id)
                e = "voacapl returned %s. Can't continue." % ret
                dialog = Gtk.MessageDialog(self.main_window, Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, e )
                dialog.run()
                dialog.destroy()
                return -1
            self.statusbar.pop(self.area_context_id)

            s = os.path.join(os.path.expanduser("~"), 'itshfbc','areadata','pyArea.voa')
            graph = VOAAreaPlotGUI(s, parent=self.main_window, enable_save=True, datadir=self.datadir)
            graph.quit_application()

        #P2P Predictions follow
        if button == self.p2prunbt:
            iter = self.p2pmethodcb.get_active_iter()
            method = self.p2pmethodcb.get_model().get_value(iter, 0)
            run_type = 'c' if self.p2pcircuitckb.get_active() else 'g'

            _coeff = 'CCIR' if (self.model_combo.get_active()==0) else 'URSI88'
            _path = VOADatFile.SHORT_PATH if (self.path_combo.get_active()==0) else VOADatFile.LONG_PATH


            input_filename = 'voacapg.dat' if run_type == 'g' else  'voacapx.dat'
            output_filename = 'voacapg.out' if run_type == 'g' else 'voacapx.out'
            data_file_format = VOADatFile.GRAPHICAL_FORMAT if run_type == 'g' else VOADatFile.CIRCUIT_FORMAT
            df = VOADatFile(self.itshfbc_path + os.sep + 'run'  + os.sep + input_filename)
            voacapl_args = self.itshfbc_path + ' ' + input_filename + ' ' + output_filename
            df.set_title([_('File generated by voacap-gui (www.qsl.net/hz1jw)'), _('File created: ')+datetime.datetime.now().strftime('%X %a %d %b %y')])
            df.set_linemax(55)
            #method = method if rt == 'g' else c_method
            df.set_method(method)
            df.set_coeffs(_coeff)
            df.set_sites(HamLocation(self.tx_lat_spinbutton.get_value(),
                                    self.tx_lon_spinbutton.get_value(),
                                    self.tx_site_entry.get_text()),
                        HamLocation(self.rx_lat_spinbutton.get_value(),
                                    self.rx_lon_spinbutton.get_value(),
                                    self.rx_site_entry.get_text()), _path)
            df.set_system(self.tx_power_spinbutton.get_value()/1000.0,\
                            abs(self.mm_noise_spinbutton.get_value()),\
                            self.min_toa_spinbutton.get_value(),\
                            self.reliability_spinbutton.get_value(),\
                            self.snr_spinbutton.get_value(),\
                            self.mpath_spinbutton.get_value(),\
                            self.delay_spinbutton.get_value())
            if run_type == 'c':
                # The frequencies are only applicable when performing text based predictions.
                # voacap can accept up to 11 entries in the list.
                # entries may be specified up to 3 decimal places.
                # longer lists, additional precision will be truncated
                # by the set_frequency_list method.
                # (The example freqs below are PSK31 calling freqs...)
                #   df.set_frequency_list((3.580, 7.035, 10.140, 14.070, 18.1, 21.08, 28.12))
                freqs = []
                model = self.p2pfreq_tv.get_model()
                iter = model.get_iter_first()
                while iter:
                    try:
                        freqs.append(float(model.get_value(iter, self.p2pfreq_tv_idx_freq)))
                    except:
                        pass
                    iter = model.iter_next(iter)
                df.set_frequency_list(tuple(freqs))

            df.set_antenna(VOADatFile.TX_ANTENNA, self.tx_antenna_path.ljust(21),
                self.tx_bearing_spinbutton.get_value(),
                self.tx_power_spinbutton.get_value()/1000.0)
            df.set_antenna(VOADatFile.RX_ANTENNA, self.rx_antenna_path.ljust(21),
                self.rx_bearing_spinbutton.get_value())
            df.set_fprob(self.foe_spinbutton.get_value(),
                self.fof1_spinbutton.get_value(), self.fof2_spinbutton.get_value(),
                self.foes_spinbutton.get_value())
            # ssn_list is a list of tuples (day, month, year, ssn)
            ssn_list = []
            model = self.p2pmy_tv.get_model()
            iter = model.get_iter_first()
            day = 0
            while iter:
                if self.p2pusedayck.get_active():
                    day = model.get_value(iter, self.p2pmy_tv_idx_day)
                    if day:
                        df.set_coeffs('URSI88')
                month = model.get_value(iter, self.p2pmy_tv_idx_month_i)
                year = model.get_value(iter, self.p2pmy_tv_idx_year)
                ssn = self.ssn_repo.get_ssn(month, year)
                if not ssn:
                    e = _("Can't find SSN number for <%(m)s>-<%(y)s>. Can't continue without all SSNs.") % {'m':month, 'y':year}
                    dialog = Gtk.MessageDialog(self.main_window,
                        Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                        Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, e )
                    dialog.run()
                    dialog.destroy()
                    return -1
                ssn_list.append((day, month, year, ssn))
                iter = model.iter_next(iter)
            df.set_ssn(ssn_list)
            df.write_file(data_file_format)

            try:
                retcode = subprocess.call("voacapl -s " + voacapl_args, shell=True)
                """
                Return Codes:
                0 - Success
                127 - error while loading shared libraries
                """
                if retcode == 0:
                    if run_type == 'c':
                        result_dialog = VOATextFileViewDialog(file=self.itshfbc_path+os.sep+'run'+os.sep+output_filename,
                                    datadir=self.datadir,
                                    parent=self.main_window)
                        return_code = result_dialog.run()
                    if run_type == 'g':
                        graph = VOAP2PPlotGUI(self.itshfbc_path+os.sep+'run'+os.sep+output_filename,
                            parent=self.main_window,
                            datadir=self.datadir)
                        graph.quit_application()
                else:
                    self.show_msg_dialog("Error", "Voacapl error code: {:d}".format(retcode), msg_type="ERROR")

            except OSError as e:
                    print("Voacapl execution failed:", e)


    def show_yelp(self, widget):
        #subprocess.call(["yelp", os.path.join(self.datadir, "help", "C", "voacapgui.xml")])
        Gtk.show_uri(None, "ghelp:voacapgui", Gdk.CURRENT_TIME)

    def show_about_dialog(self, widget):
        about = Gtk.AboutDialog(parent=self.main_window,
                        program_name = "voacapgui",
                        version = self.pythonprop_version,
                        authors = (("J.Watson (HZ1JW/M0DNS)", "Fernando M. Maresca (LU2DFM)")),
                        comments = (_("A voacap GUI")),
                        website = "http://www.qsl.net/hz1jw",
                        logo = (GdkPixbuf.Pixbuf.new_from_file(os.path.join(self.datadir, "ui", "voacap.png"))))
        about.run()
        about.destroy()

    def build_new_template_file(self):
        fn = os.path.join(self.prefs_dir,'area_templ.ex')
        s = _('''# rough format for area plot templates:
# lines starting with # are ignored
# each line consist in three values separated by spaces
# each template is preceded by a name enclosed in square brackets:
# [template name]
# tags
# month utchour freq
# 11    22      14.250
# month: number month, 1=January
# utchour: UTC time HOUR, 00 to 23
# freq: frequecy in MHz
# example: all months at midnight on 14.100 MHz
[All months midnight 14.100 Mhz]
#year month utchour freq
2010      01      00      14.10
2010      02      00      14.10
2010      03      00      14.10
2010      04      00      14.10
2010      05      00      14.10
2010      06      00      14.10
2010      07      00      14.10
2010      08      00      14.10
2010      09      00      14.10
2010      10      00      14.10
2010      11      00      14.10
2010      12      00      14.10

[All months at 1600z 7.500 MHz]
#month utchour freq
2010      01      16      7.5
2010      02      16      7.5
2010      03      16      7.5
2010      04      16      7.5
2010      05      16      7.5
2010      06      16      7.5
2010      07      16      7.5
2010      08      16      7.5
2010      09      16      7.5
2010      10      16      7.5
2010      11      16      7.5
2010      12      16      7.5
\n
''')
        with open(fn, 'w') as templates_def_fd:
            templates_def_fd.write(s)
        self.area_templates_file = fn

    def get_vgz_filename(self):
        dialog = Gtk.FileChooserDialog("Please select a vgz file", self.main_window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))
        filter_vgz = Gtk.FileFilter()
        filter_vgz.set_name(".vgz files")
        filter_vgz.add_pattern("*.vgz")
        dialog.add_filter(filter_vgz)
        dialog.set_default_size(800, 400)

        response = dialog.run()
        vgzip_file = ""
        if response == Gtk.ResponseType.OK:
            vgzip_file = dialog.get_filename()
        dialog.destroy()
        return vgzip_file


    def open_vgz_file(self,widget):
        vgzip_file = self.get_vgz_filename()
        if vgzip_file != "":
            try:
                graph = VOAAreaPlotGUI(vgzip_file,
                        parent=self.main_window,
                        enable_save=False,
                        datadir=self.datadir)
                graph.quit_application()
            except zipfile.BadZipFile as e:
                self.show_msg_dialog("VGZ Error", "Error opening {:s}".format(vgzip_file), msg_type="ERROR")

    """
    # This is on hold until I figure out a way to save the year along with
    # the voa file (maybe a comment?)
    def restore_from_voa_file(self, widget):
        vgzip_file = self.get_vgz_filename()
        voa_file = VOAFile(vgzip_file)
        voa_file.parse_file()
        self.tx_site_entry.set_text(voa_file.get_tx_label())
        self.tx_lat_spinbutton.set_value(voa_file.get_tx_lat())
        self.tx_lon_spinbutton.set_value(voa_file.get_tx_lon())
        self.gridsizespinbutton.set_value(voa_file.get_gridsize())
        self.tx_antenna_entry.set_text(voa_file.get_txAntenna())
        self.tx_antenna_path = voa_file.get_txAntenna()

        self.tx_bearing_spinbutton.set_value(voa_file.get_txBearing())
        self.tx_power_spinbutton.set_value(voa_file.get_txPower() * 1000)

        self.area_rect=voa_file.get_area_rect()
        self.area_label.set_text(self.area_rect.get_formatted_string())

        #self.area_add_tv_rows([(year, month_i, utc, freq)])
        self.area_add_tv_rows([(2018, 5, 2, 15.310)])


        self.mm_noise_spinbutton.set_value(voa_file.get_xnoise())
        self.min_toa_spinbutton.set_value(voa_file.get_amind())
        self.reliability_spinbutton.set_value(voa_file.get_xlufp())
        self.snr_spinbutton.set_value(voa_file.get_rsn())
        self.mpath_spinbutton.set_value(voa_file.get_pmp())
        self.delay_spinbutton.set_value(voa_file.get_dmpx())

        self.foe_spinbutton.set_value(voa_file.get_psc1())
        self.fof1_spinbutton.set_value(voa_file.get_psc2())
        self.fof2_spinbutton.set_value(voa_file.get_psc3())
        self.foes_spinbutton.set_value(voa_file.get_psc4())

        #self.open_vgz_file(vgzip=vgzip_file)
        """

    # INFO, WARNING & ERROR messages
    def show_msg_dialog(self, msg_title, msg_body, msg_type='INFO'):
        dialog = Gtk.MessageDialog(self.main_window,
            0,
            getattr(Gtk.MessageType, msg_type),
            Gtk.ButtonsType.CANCEL, msg_title)
        dialog.format_secondary_text(msg_body)
        dialog.run()
        dialog.destroy()


    def quit_application(self, widget):
        self.save_user_prefs()
        Gtk.main_quit
        sys.exit(0)

    def run(self, argv):
        print("run")
        self.connect('activate', self.on_activate)
        return super(VOACAP_GUI, self).run(argv)

def main(argv, datadir="", pythonprop_version="dev"):
    if not datadir:
        print("no datadir defined, using current dir")
        datadir = os.path.dirname(os.path.realpath(sys.argv[0]))
    app = VOACAP_GUI(datadir=datadir, pythonprop_version=pythonprop_version)
    try:
        Gtk.main()
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv)
