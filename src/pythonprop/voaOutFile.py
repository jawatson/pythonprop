#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#
# File: voaOutFile.py
# Version: 10Jul09
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
# Contact jimwatson /at/ mac /dot/ com
#
# A small class to encapsulate reads of an 'out' file produced by
# voacap.

# This file is in the early stages of development.  There are a number
# of routines in voaP2PPlot that need to be migrated over to here.

import os.path
import sys, re
import numpy as np
import codecs

class VOAOutFile:

    filename = ''
    groups = [] # holds (group_description_str, muf_graph_data) tuples

    image_re_patterns = ['None', 'MUFday', 'REL', 'SNR', 'S DBW']

    def __init__(self, fn, time_zone=0, data_type=0, quiet=True):
        self.filename = fn
        self.data_type = data_type
        self.quiet = quiet
        self.time_zone = time_zone
        if os.path.isfile(self.filename):
            self.parse_file()
        else:
            print("Unable to find file: ", self.filename)
        return

    def parse_file(self):
        self.groups = []
        muf_pattern = re.compile(r"^\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+([-+]?\d*\.?\d+)\s*$")
        self.group_pattern = re.compile(r'COMMENT\s+GROUP\s+(\d+)[:\s]+(.*)')
        image_pattern = re.compile(r'%s\s*$' % self.image_re_patterns[self.data_type])
        #print self.image_re_patterns[self.data_type]
        float_pattern = re.compile(r"\d+")

        _current_group = -1
        try:
            self.out_file = codecs.open(self.filename, "r", "utf-8")
            if not self.quiet:
                print("Opening: ", self.filename)
            #Initialise the variables here in case the input file
            #doesn't contain any 'COMMENT GROUP cards
            #Thanks to Dhivya Raj for spotting this bug
            _fot = np.zeros(25, float)
            _muf = np.zeros(25, float)
            _hpf = np.zeros(25, float)
            _image_buffer = np.zeros([29, 25], float)
            _group_name = ''
            _group_info = ''

            for line in self.out_file:
                _group_match = self.group_pattern.search(line) #start a new group
                if _group_match:
                    if _current_group > 0:
                        #todo this little block is repeated at the end as well
                        #do the timeshifts when reading in the data
                        if self.time_zone >= 0:
                            _image_buffer[0:,0]=_image_buffer[0:,24]
                        else:
                            _image_buffer[0:,24]=_image_buffer[0:,0]
                        #down to here is repeated.... sort this out before release
                        self.groups.append((_group_name, _group_info, _fot, _muf, _hpf, _image_buffer))

                    _group_name = ''
                    _group_info = ''
                    #_utc = range(0, 25)

                    _fot = np.zeros(25, float)
                    _muf = np.zeros(25, float)
                    _hpf = np.zeros(25, float)
                    _image_buffer = np.zeros([29, 25], float)

                    _current_group = int(_group_match.group(1))
                    _group_name = (_group_match.group(1)+': '+_group_match.group(2)).strip()
                    # Wind forward two lines and read in the description
                    for i in np.arange(0,2):
                        next(self.out_file)
                    for i in np.arange(0,6):
                        _group_info = _group_info + next(self.out_file)

                if line.find("FREQ") == 67:
                    lastFreqLine = line

                _muf_match = muf_pattern.match(line)
                if _muf_match:
                    _hour = self.get_adjusted_hour(int(float(_muf_match.group(1))))
                    _fot[_hour] = float(_muf_match.group(3))
                    _muf[_hour] = float(_muf_match.group(6))
                    _hpf[_hour] = float(_muf_match.group(4))
                    if self.time_zone >= 0:
                        _fot[0] = _fot[-1]
                        _muf[0] = _muf[-1]
                        _hpf[0] = _hpf[-1]
                    else:
                        _muf[-1] = _muf[0]
                        _fot[-1] = _fot[0]
                        _hpf[-1] = _hpf[0]


                if image_pattern.search(line):
                    freqEntries = lastFreqLine.split()
                    for x in range(0, 12):
                        """Values start at char 11 and are 5 chars wide (we
                        ignore the first value which is the MUF.
                        """
                        try:
                            val = float(line[11+(5*x):16+(5*x)])
                        except ValueError:
                            break
                        if float(freqEntries[x+2])>=2.0:
                            _hour = self.get_adjusted_hour(int(float(freqEntries[0])))
                            _image_buffer[int(float(freqEntries[x+2]))-2][_hour] = val
                            #print("N {:d} {:d} = {:.2f}".format(int(float(freqEntries[x+2])), _hour, val))
                """
                if image_pattern.search(line):
                    #print line
                    imgEntries = line.split()
                    freqEntries = lastFreqLine.split()
                    for x in np.arange(1, len(imgEntries)):
                        if (float_pattern.search(imgEntries[x]) and (float(freqEntries[x+1])>=2.0)):
                            _hour = self.get_adjusted_hour(int(float(freqEntries[0])))
                            _image_buffer[int(float(freqEntries[x+1]))-2][_hour] = float(imgEntries[x])
                            print("O {:d} {:d} = {:.2f}".format(int(float(freqEntries[x+1])), _hour, float(imgEntries[x])))
                """

            if self.time_zone >= 0:
                _image_buffer[0:,0]=_image_buffer[0:,24]
            else:
                _image_buffer[0:,24]=_image_buffer[0:,0]

            self.groups.append((_group_name, _group_info, _fot, _muf, _hpf, _image_buffer))

        # The following lines require Python 2.5
        except IOError:
            print(_("Error opening/reading file "), self.filename)
            sys.exit(1)
        finally:
            if not self.quiet:
                print("Closing: ", self.filename)

        if _current_group == -1:
            print("****************************************************")
            print("Warning: No COMMENT GROUP cards found in input file.")
            print("Please refer to the manpage for correct file format.")
            print("****************************************************")

    def get_number_of_groups(self):
        return len(self.groups)

    # Returns a list of titles (may be used for populating a combobox)
    def get_group_titles(self):
        _titles = []
        for (_group_name, _group_info, _fot, _muf, _hpf, _image_buffer) in self.groups:
            _titles.append(_group_name)
        return _titles

    def get_group_data(self, group_number):
        return self.groups[group_number]

    def get_reliability_list(self, channel):
        rel_pattern = re.compile(r" REL\s*$")
        self.out_file.seek(0)
        rel_list = []
        for line in self.out_file:
            _group_match = rel_pattern.search(line) #start a new group
            if _group_match:
                tokens = line.split()
                rel_list.append(float(tokens[channel+1]))
        #print rel_list
        return rel_list

## Internal Methods follow

    def get_adjusted_hour(self, hour):
        hour = hour + self.time_zone
        if hour > 24:
            hour = hour - 24
        elif hour < 0:
            hour = hour + 24
        return hour
