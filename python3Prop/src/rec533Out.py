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

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
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
        self.plot_rect = VOAAreaRect() # default is global
        self.lat_step = 5.0
        self.lon_step = 5.0

    def __iter__(self):
        pass

    def __next__(self):
        pass

    def get_plot_data(self, hour, freq):
        num_pts_lat = ((self.plot_rect.get_ne_lat() - self.plot_rect.get_sw_lat()) / self.lat_step) + 1
        print ("num_pts_lat = ", num_pts_lat)
        num_pts_lon = ((self.plot_rect.get_ne_lon() - self.plot_rect.get_sw_lon()) / self.lon_step) + 1
        print ("num_pts_lon = ", num_pts_lon)
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
                        #print (float(row[3]))
                        #print (self.plot_rect.get_sw_lat())
                        #print ("lat_grid_pos =", lat_grid_pos)
                        lon_grid_pos = (int(float(row[4])-self.plot_rect.get_sw_lon()) / self.lon_step)
                        #print ("lon_grid_pos =", lon_grid_pos)
                        points[lat_grid_pos][lon_grid_pos] = float(row[8])
                        #print (lat_grid_pos, lon_grid_pos, float(row[8]))

        finally:
            f.close()
        return (points,lons,lats,num_pts_lon,num_pts_lat)

'''
The following function is for testing purposes only.
'''
if __name__ == "__main__":
    r533 = REC533Out("area.out")
    points,lons,lats,num_pts_lon,num_pts_lat = r533.get_plot_data('01', '3.52')

    plt.figure(figsize=(12,6))
    m = Basemap(projection='cyl', resolution='l')
    m.drawcoastlines(color='black')
    m.drawcountries(color='grey')
    m.drawmapboundary(color='black', linewidth=1.0)
    # draw lat/lon grid lines every 30 degrees.
    m.drawmeridians(np.arange(0,360,30))
    m.drawparallels(np.arange(-90,90,30))

    print ("points: ", points.shape)
    print ("lons: ", len(lons))
    print ("lats: ", len(lats))
    print ("num_lon: ", num_pts_lon)
    print ("num_lat: ", num_pts_lat)
    X,Y = np.meshgrid(lons, lats)
    print ("X: ", X.shape)

    print ("Y: ", Y.shape)

    im1 = m.pcolormesh(X, Y, points, shading='gouraud', cmap=plt.cm.jet, latlon=True)
    #cb = m.colorbar(im1,"bottom", size="5%", pad="2%")
    #plt.title('Test ITU Image')

    plt.savefig('foo.png', dpi=1200, bbox_inches='tight')

    plt.show()
