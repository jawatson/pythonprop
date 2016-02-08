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


import re
import sys, getopt
import os

class VOAMeth26Out:

    m26_pattern = re.compile(r"^\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+([-+]?\d*\.?\d+)\s*$") 
        
    new_group_pattern = re.compile(r"^\f.+METHOD 26")

    # Public accessors
    def __init__(self, filename, quiet=False):
        self.filename = filename
        self.quiet = quiet

        self.num_groups = 0
        # Values are stored values in multidimensional lists
        self.gmt_list = []
        self.muf_list = []
        self.hpf_list = []
        self.fot_list = []
        if os.path.isfile(self.filename):
            self.parse_file()
        else:
            print("Unable to find file: ", self.filename)
        return

    """
    Returns a list of the times in the file, adjusted by the specified 
    timezone 'tz'.
    """
    def get_hours(self, group=0):
        return self.gmt_list[group]

    """ Returns a list of tuples (hour, fot) of the FOT.

        The list is up to 24 elements long with values correlating to 
        the times returned by get_hours().
    """
    def get_FOT(self, group=0, tz=0):
        return self.fot_list[group]

    def get_FOT_as_tuples(self, group=0, tz=0):
        return list(zip(self.gmt_list[group], self.fot_list[group]))

    def get_HPF(self, group=0, tz=0):
        return self.hpf_list[group]

    def get_HPF_as_tuples(self, group=0, tz=0):
        return list(zip(self.gmt_list[group], self.hpf_list[group]))

    def get_MUF(self, group=0, tz=0):
        return self.muf_list[group]

    def get_MUF_as_tuples(self, group=0, tz=0):
        return list(zip(self.gmt_list[group], self.muf_list[group]))

    def get_number_groups(self):
        return len(self.gmt_list)

    # Internal methods
    # Method 26 files are all on one page.  Each page starts with the line;
    # CCIR Coefficients         METHOD 26   VOACAP L 14.0905W  PAGE   1
    def parse_file(self):
        try:
            with open(self.filename) as f:
                group_number = -1
                for line in f:
                    if self.new_group_pattern.match(line):
                        # Start of a new group
                        self.gmt_list.append([])
                        self.muf_list.append([])
                        self.hpf_list.append([])
                        self.fot_list.append([])
                        group_number = group_number + 1
                    if (group_number > -1):
                        match = self.m26_pattern.match(line)
                        if match:
                            # Found a line of values
                            # we should call another prociedure here parse_values()
                            #print line
                            gmt = int(float(match.group(1)))
                            fot = float(match.group(3))
                            hpf = float(match.group(4))                        
                            muf = float(match.group(6)) 
                            self.gmt_list[group_number].append(gmt)                        
                            self.fot_list[group_number].append(fot)                    
                            self.hpf_list[group_number].append(hpf) 
                            self.muf_list[group_number].append(muf) 

        except IOError:
            print(_("Error opening/reading file "), self.filename)
            sys.exit(1)
        finally:
            if not self.quiet:
                print("Closing: ", self.filename)            

## Used for testing only
def main(argv):
    # parse command line options
    inputfile = ""
    try:
        opts, args = getopt.getopt(argv, "hi:", ["ifile="])
    except getopt.error as msg:
        print(msg)
        print("for help use --help")
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-i", "--ifile"):
            inputfile = a

    of = VOAMeth26Out(inputfile)
    for group in range(0, of.get_number_groups()):
        print("***")
        print(of.get_MUF(group=group))
        for group in range(0, of.get_MUF(group=group)):
            print(of.get_MUF(group))  

if __name__ == "__main__":
    main(sys.argv[1:])
    
