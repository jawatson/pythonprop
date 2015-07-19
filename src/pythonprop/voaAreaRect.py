#! /usr/bin/env python
#
# File: voaAreaRect
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

# A small class to encapsulate a geographic area as a rectangle. 
#

class VOAAreaRect:

    sw_lat = -90.0
    sw_lon = -180.0

    ne_lat = 90.0
    ne_lon = 180.0

    def __init__(self, sw_lat=-90.0, sw_lon=-180.0, ne_lat=90.0, ne_lon=180.0):
        # Check that the rectangle is the right way round
        self.sw_lat = min(sw_lat, ne_lat)
        self.sw_lon = min(sw_lon, ne_lon)
        self.ne_lat = max(sw_lat, ne_lat)
        self.ne_lon = max(sw_lon, ne_lon)
        # Check values are in range
        self.sw_lat = max(self.sw_lat, -90.0)
        self.sw_lon = max(self.sw_lon, -180.0)
        self.ne_lat = min(self.ne_lat, 90.0)
        self.ne_lon = min(self.ne_lon, 180.0)


    def get_sw_lat(self): return self.sw_lat
    def get_sw_lon(self): return self.sw_lon
    def get_ne_lat(self): return self.ne_lat
    def get_ne_lon(self): return self.ne_lon

    def get_sw(self): return self.sw_lat, self.sw_lon


    def set_sw(self, sw_lat=0.0, sw_lon=0.0) :
        self.sw_lat = sw_lat
        self.sw_lon = sw_lon


    def get_ne(self): return self.ne_lat, self.ne_lon


    def set_ne(self, ne_lat=90.0, ne_lon=180.0) :
        self.ne_lat = ne_lat
        self.ne_lon = ne_lon

    def set_ne_lat(self, ne_lat=90.0):
        self.ne_lat = ne_lat

    def set_ne_lon(self, ne_lon=180.0):
        self.ne_lon = ne_lon

    def set_sw_lat(self, sw_lat=-90.0):
        self.sw_lat = sw_lat

    def set_sw_lon(self, sw_lon=-180.0):
        self.sw_lon = sw_lon


    def get_rect(self): return self.sw_lat, self.sw_lon, self.ne_lat, self.ne_lon

    def get_lon_delta(self): return self.ne_lon - self.sw_lon

    def get_lat_delta(self): return self.ne_lat - self.sw_lat
    
    def get_formatted_string(self):
        return u"(%i\N{DEGREE SIGN}N, %i\N{DEGREE SIGN}E), (%i\N{DEGREE SIGN}N, %i\N{DEGREE SIGN}E)" \
        			% (int(round(self.sw_lat)), int(round(self.sw_lon)), int(round(self.ne_lat)), int(round(self.ne_lon)))
    def get_formatted_ne_latitude(self):
        return "%.2f" % self.ne_lat

    def get_formatted_ne_longitude(self):
        return "%.2f" % self.ne_lon

    def get_formatted_sw_latitude(self):
        return "%.2f" % self.sw_lat

    def get_formatted_sw_longitude(self):
        return "%.2f" % self.sw_lon

    def contains(self, lat, lon):
        if ((lat >= self.sw_lat) and (lat <= self.ne_lat) and 
                (lon >= self.sw_lon) and (lon <= self.ne_lon)):
            return True
        else:
            return False
    


 
