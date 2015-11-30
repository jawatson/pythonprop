#! /usr/bin/env python
#
# File: rec533Out.py
#
# Copyright (c) 2015 J.Watson (jimwatson@mac.com)
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

import csv

import numpy as np

from voaAreaRect import VOAAreaRect

class REC533Out:
    '''
    A small class to encapsulate files produced by the ITURHFProp
    application.  These file may contain a number of sets of plot data.
    These may be accessed directly or via an iterator.

    Plots sets for different values of hour and frequency may be contained
    in a single REC533 Out file.

    Each entry starts with the month, hour, frequency.  User defined values
    follow.
    '''

    filename = ""

    def __init__(self, filename):
        self.filename = filename
        # todo each of the following parameters should be read from the outfile
        self.plot_rect = VOAAreaRect()
        self.lat_step = 5.0
        self.lon_step = 5.0
        #self.parse_input_params()
        self.datasets = self.build_dataset_list()
        print ("Found ",len(self.datasets), " datasets")

        with open(filename, 'r') as f:
            for month, hour, freq, offset in self.datasets:
                f.seek(offset)
                print(f.readline().strip())


    def build_dataset_list(self):
        datasets = []
        month = ''
        hour = ''
        freq = ''
        idx = 0
        calculated_parameters_section = False
        with open(self.filename) as f:
            for line in f:
                if "**** Calculated Parameters ****" in line:
                    calculated_parameters_section = True
                elif calculated_parameters_section:
                    params = line.split(',')
                    if len(params) > 3:
                        if (month != params[0]) or (hour != params[1]) or (freq != params[2]):
                            month = params[0]
                            hour = params[1]
                            freq =params[2]
                            datasets.append((month, hour, freq, idx))
                            print (month, hour, freq, idx)
                idx += len(line)+1
        return datasets



    def __iter__(self):
        pass

    def __next__(self):
        pass

    def get_plot_data(self, hour, freq):
        num_pts_lat = ((self.plot_rect.get_ne_lat() - self.plot_rect.get_sw_lat()) / self.lat_step) + 1
        num_pts_lon = ((self.plot_rect.get_ne_lon() - self.plot_rect.get_sw_lon()) / self.lon_step) + 1
        points = np.zeros([num_pts_lat, num_pts_lon], float)

        lons = np.arange(self.plot_rect.get_sw_lon(),
                    self.plot_rect.get_ne_lon()+1,
                    self.lon_step)
        lats = np.arange(self.plot_rect.get_sw_lat(),
                    self.plot_rect.get_ne_lat()+1,
                    self.lat_step)
        f = open(self.filename, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 3:
                    if row[1].strip()==hour and row[2].strip()==freq:
                        #print (row)
                        #todo remove the hardcodes values of 3, 4 and 8 below
                        lat_grid_pos = (int(float(row[3])-self.plot_rect.get_sw_lat()) / self.lat_step)
                        lon_grid_pos = (int(float(row[4])-self.plot_rect.get_sw_lon()) / self.lon_step)
                        points[lat_grid_pos][lon_grid_pos] = float(row[8])
        finally:
            f.close()
        return (points,lons,lats,num_pts_lon,num_pts_lat)
