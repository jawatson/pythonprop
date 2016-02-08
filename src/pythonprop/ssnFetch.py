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
from gi.repository import Gtk
import os.path
import shutil
import time
from datetime import datetime
from datetime import date
from datetime import timedelta

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
    """ This is a small class to handle retrieving ssn data from a remote location.
    The ssn data is saved as the file 'table_international-sunspot-numbers_monthly-predicted.txt' in the users configuration
    folder.  If this file is found, it will be read.  If this file does not exist,
    the file will be retrieved from the internet.

    WARNING: In the current version the connection to the internet is automatic and
    is perfomred with the users explicit consent.
    """
    ssn_dic = {}
    ssn_pattern = re.compile('\s+(\d\d\d\d)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+')
    #ssn_url = "ftp://ftp.ngdc.noaa.gov/STP/SOLAR_DATA/SUNSPOT_NUMBERS/sunspot.predict"
    ssn_url = "ftp://ftp.ngdc.noaa.gov/STP/space-weather/solar-data/solar-indices/sunspot-numbers/predicted/table_international-sunspot-numbers_monthly-predicted.txt"
    save_location = ""
    s_bar = None



    def __init__(self, parent = None, save_location=None, s_bar=None):
        """Progress notes will be sent to the status bar
        defined by s_bar.  This may be replaced with a
        statusbar manager in later versions.'
        """
        #The model is structured as follows
        # 0 - year as text
        # 1-12: monthly ssn as text
        # 13-25: forground colour (used to highlight current month
        columns = [GObject.TYPE_STRING]*26
        Gtk.ListStore.__init__( self, *columns )
        self.save_location = save_location
        self.s_bar = s_bar
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
                self.update_ssn_file()
            else:
                raise NoSSNData("User Cancelled SSN Fetch")
        age = time.time() - self.get_ssn_mtime()
        #print "File was saved " + str(age) + "seconds ago."
        self.read_ssn_file()


    def progress_reporthook(self, count, block_size, total_size):
        fraction = float(count * block_size) / float(total_size)
        fraction = min(fraction, 1.0) * 100.0
        msg_str = _("Transferring Data: ")+str(fraction)+"%"
        print(msg_str)
        if self.s_bar:
            context_id = self.s_bar.get_context_id("ssn_data_transfer")
            self.s_bar.push(context_id, msg_str)
            while Gtk.events_pending():
                Gtk.main_iteration()

    def update_ssn_file(self):
        print("*** Connecting to " + self.ssn_url)
        if self.s_bar:
            context_id = self.s_bar.get_context_id("ssn_data_connecting")
            self.s_bar.push(context_id, _("Connecting to ") + self.ssn_url)
            while Gtk.events_pending():
                Gtk.main_iteration()
        try:
            f_name, header = urllib.request.urlretrieve(self.ssn_url, reporthook=self.progress_reporthook)
            shutil.copyfile(f_name, self.save_location)
            # todo delete the temp
            print("*** Disconnected from internet ***")
            if self.s_bar:
                context_id = self.s_bar.get_context_id("ssn_data_done")
                self.s_bar.push(context_id, _("Done"))
                while Gtk.events_pending():
                    Gtk.main_iteration()
            self.read_ssn_file()
        except:
            print("*** Failed to retrieve data ***")
            if self.s_bar:
                context_id = self.s_bar.get_context_id("ssn_data_done")
                self.s_bar.push(context_id, _("Error: Unable to retrieve data"))
                while Gtk.events_pending():
                    Gtk.main_iteration()


    def read_ssn_file(self):
        self.clear()
        gmt_time = time.gmtime()
        try:
            f = open(self.save_location)
            for line in f:
                m = self.ssn_pattern.match(line)
                if m:
                    self.ssn_dic[int(m.group(1))] = m.group(2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
                    _fg_colour = ["regular"]*13
                    _ssn_values = [m.group(1),
                                m.group(2),
                                m.group(3),
                                m.group(4),
                                m.group(5),
                                m.group(6),
                                m.group(7),
                                m.group(8),
                                m.group(9),
                                m.group(10),
                                m.group(11),
                                m.group(12),
                                m.group(13)]

                    if _ssn_values[0] == str(gmt_time.tm_year):
                        _fg_colour[gmt_time.tm_mon] = 'bold'
                    self.append(_ssn_values + _fg_colour)
            f.close()
        except:
            print("*** Error reading data file ***")
            self.clear()
            #todo check that we clear the dictionary as well
            print(sys.exc_info()[0])
            if self.s_bar:
                context_id = self.s_bar.get_context_id("ssn_data_read_err")
                self.s_bar.push(context_id, _("Error: Unable to read SSN data"))
                while Gtk.events_pending():
                    Gtk.main_iteration()


    def get_data_range(self):
        """Returns a tuple (first, last) of the years covered by the data.
        """
        keys = list(self.ssn_dic.keys())
        keys.sort()
        return (keys[0], keys[-1])


    def get_ssn(self, month, year):
        if self.ssn_dic:
            month_list = self.get_ssn_list(year)
            try:
                return month_list[int(month)-1]
            except:
                pass
        return None


    def get_plotting_data(self):
        """Returns a pair of lists (date & ssn values) suitable for plotting with
        matplotlib.
        """
        d_list = []
        ssn_list = []
        first, last = self.get_data_range()
        for year in range(first, last+1):
            ssns = self.get_ssn_list(year)
            month = 1
            for ssn in ssns:
                d = date(year, month, 15)
                d_list.append(d)
                ssn_list.append(ssn)
                month = month + 1
        return d_list, ssn_list


    def get_ssn_list(self, year=datetime.utcnow().year):
        if year in self.ssn_dic:
            return self.ssn_dic[year]
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


#short test routine
def main():
    s = SSNFetch(save_location="fetch_test.txt")
    years = (2006, 2007, 2008, 2009)
    for year in years:
        print('Year = ', year, '.  SSN = ', s.get_ssn_list(year))
    print('Ths years list is ', s.get_ssn_list())
