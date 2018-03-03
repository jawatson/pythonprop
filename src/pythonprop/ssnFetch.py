#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#
# File: ssnFetch.py
#
# Copyright (c) 2009 J.A.Watson
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
# Contact jimwatson @@ mac.com
#
# returns a list of sunspot numbers for the given year
#
import urllib.request, urllib.parse, urllib.error, re
import os.path
import shutil
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import csv
import json
import io
import urllib.request

import gettext, locale, sys

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

class NoSSNData(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SSNFetch(Gtk.ListStore):
    """ This is a small class to handle retrieving ssn data from a remote
    location.

    Data is retreived from the following locations;

    http://sidc.oma.be/silso/INFO/snmstotcsv.php

    http://www.sidc.be/silso/FORECASTS/prediML.txt

    The ssn data is parsed and saved into a single file named ssn.json
    in the users configuration folder.  If this file is found, it is
    opened and read.  If this file does not exist, the file will be
    retrieved from the Internet.

    WARNING: In the current version the connection to the internet
    is automatic and is performed without the users explicit consent.
    """
    # ssn datamodel
    ssn_dm = {}
    final_url = 'http://sidc.oma.be/silso/INFO/snmstotcsv.php'
    pred_url = 'http://www.sidc.be/silso/FORECASTS/prediML.txt'
    out_fn = 'ssn.json'
    SSN_START_YEAR = 2005
    save_location = ""
    s_bar = None

    now = datetime.utcnow()
    ssn_data = {'retrieved': now.timestamp(), 'sources':[final_url, pred_url], 'ssn':{}}

    def __init__(self, parent=None, save_location=None, s_bar=None, s_bar_context=None):
        """
        Progress notes will be sent to the status bar  defined by s_bar.
        This may be replaced with a statusbar manager in later versions.
        """
        #The model is structured as follows
        # 0 - year as text
        # 1-12: monthly ssn as text
        columns = [GObject.TYPE_STRING]*13
        Gtk.ListStore.__init__( self, *columns )

        self.save_location = save_location
        self.s_bar = s_bar
        self.s_bar_context = s_bar_context
        # if no file exists, grab it
        if not os.path.isfile(self.save_location):
            e = _("No SSN Data Found")
            dialog = Gtk.MessageDialog(flags=Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.OK_CANCEL,
                    message_format=e,
                    parent = parent)
            dialog.format_secondary_text(_('This application needs to connect \
to the internet to retrieve SSN data. Select OK to proceed.'))
            response = dialog.run()
            dialog.destroy()
            if (response == Gtk.ResponseType.OK):
                self.build_ssn_file()
            else:
                raise NoSSNData("User Cancelled SSN Fetch")
        #age = time.time() - self.get_ssn_mtime()
        #print "File was saved " + str(age) + "seconds ago."
        self.open_ssn_file()


    def progress_reporthook(self, count, block_size, total_size):
        fraction = float(count * block_size) / float(total_size)
        fraction = min(fraction, 1.0) * 100.0
        msg_str = _("Transferring Data: ")+str(fraction)+"%"
        print(msg_str)
        if self.s_bar:
            self.s_bar.pop(self.s_bar_context)
            self.s_bar.push(self.s_bar_context, msg_str)
            while Gtk.events_pending():
                Gtk.main_iteration()

    """
    Collect values from the SIDC.  As of July 2015, these are around 45% higher
    than those previously published by NOAA.  This function apply a correction
    (1.45) to bring the values closer to the original NOAA values.
    """
    def build_ssn_file(self):
        print ("Requesting file from {:s}".format(self.final_url))
        final_ssn_data = urllib.request.urlopen(self.final_url)
        datareader = csv.reader(io.TextIOWrapper(final_ssn_data), delimiter=';')
        ssn_list = list(datareader)
        for ssn_record in ssn_list:
            year = ssn_record[0].strip()
            if (int(year) >= self.SSN_START_YEAR) and (float(ssn_record[3]) > 0):
                #print(ssn_record)
                month = str(int(ssn_record[1]))
                ssn = float("{:.1f}".format(float(ssn_record[3]) / 1.45))
                if ssn_record[0] not in self.ssn_data['ssn']:
                    self.ssn_data['ssn'].update({year:{month:ssn}})
                else:
                    self.ssn_data['ssn'][year][month] = ssn

        print ("Requesting file from {:s}".format(self.pred_url))
        response = urllib.request.urlopen(self.pred_url)
        data = response.read()
        text = data.decode('utf-8')
        #print ("Writing data to ssn.json")
        for line in text.splitlines():
            year = line[0:4]
            month = str(int(line[5:7]))
            ssn = float(line[20:25])
            ssn = float("{:.1f}".format(ssn / 1.45))
            if year not in self.ssn_data['ssn']:
                self.ssn_data['ssn'].update({year:{month:ssn}})
            else:
                self.ssn_data['ssn'][year][month] = ssn

        with open(self.save_location, 'w') as outfile:
            json.dump(self.ssn_data, outfile)

        print ("Saved to {:s}".format(self.save_location))


    def open_ssn_file(self):
        with open(self.save_location) as data_file:
            self.ssn_data = json.load(data_file)
        self.populate_liststore()


    def update_ssn_file(self):
        self.build_ssn_file()
        self.clear()
        self.open_ssn_file()


    def populate_liststore(self):
        for year in sorted(self.ssn_data['ssn'].keys()):
            _ssn_entry = [year]
            for month in range(1,13):
                if str(month) in self.ssn_data['ssn'][year]:
                    _ssn_entry.append(str(self.ssn_data['ssn'][year][str(month)]))
                else:
                    _ssn_entry.append('-')
            self.append(_ssn_entry)


    def get_data_range(self):
        """
        Returns a tuple (first, last) of the years covered by the data.
        """
        min_year = int(min(int(y) for y in self.ssn_data['ssn'].keys()))
        min_month = int(min(int(m) for m in self.ssn_data['ssn'][str(min_year)].keys()))
        ssn_start_date = date(int(min_year), int(min_month), 15)
        max_year = int(max(int(y) for y in self.ssn_data['ssn'].keys()))
        max_month = int(max(int(m) for m in self.ssn_data['ssn'][str(max_year)].keys()))
        ssn_end_date = date(int(max_year), int(max_month), 15)
        return(ssn_start_date, ssn_end_date)


    def get_ssn(self, month, year):
        if self.ssn_data:
            try:
                return self.ssn_data['ssn'][str(year)][str(month)]
            except:
                pass
        return None


    def get_plotting_data(self):
        """Returns a pair of lists (date & ssn values) suitable for plotting with
        matplotlib.
        """
        # Can't this be done with an interpreted list?
        d_list = []
        ssn_list = []
        first, last = self.get_data_range()
        for year in range(first.year, last.year+1):
            for month in range(1,13):
                d = date(year, month, 15)
                if str(month) in self.ssn_data['ssn'][str(year)]:
                    d_list.append(d)
                    ssn_list.append(self.ssn_data['ssn'][str(year)][str(month)])
                else:
                    break
        return d_list, ssn_list


    def get_ssn_list(self, year=datetime.utcnow().year):
        if str(year) in self.ssn_data['ssn']:
            return self.ssn_data['ssn'][str(year)]
        else:
            return None


    def get_ssn_mtime(self):
        if os.path.isfile(self.save_location):
            return os.path.getmtime(self.save_location)
        else:
            return 0


    def get_file_data(self):
        _mod_time = time.ctime(self.get_ssn_mtime())
        return _("SSN Data Modified: \n") + _mod_time
