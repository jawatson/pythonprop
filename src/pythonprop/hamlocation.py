#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: hamocation
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

# A small class to encapsulate a 'location' (name, lat, lon)
# Support Maidenhead loacators and 

import math 

class HamLocation:

    lon = 0.0
    lat = 0.0
    name = ''
    locator = ''
    
    SHORT_PATH = 0
    LONG_PATH = 1
    
    UNIT_KM = 0
    UNIT_MILES = 1
    
    #The following two lists are used fro mapping characters
    #to numbers in locator calculations
    lcase_letters = list(map(chr, list(range(97, 123))))
    ucase_letters = list(map(chr, list(range(65, 91))))

    def __init__(self, lat=0.0, lon=0.0, name='', locator=''):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.locator = locator
        if ((self.lat == 0.0) & (self.lon == 0.0) & (self.locator !='')) :
            # Calculate the lat lon here from the bearing
            self.lat, self.lon = self.get_latlon_from_locator(self.locator)

    def get_name(self): return self.name


    def set_name(self, name='') :
        self.name = name.strip()


    def get_latitude(self): return self.lat


    def set_latitude(self, lat=0.0) :
        #check bounds
        self.lat = lat


    def get_longitude(self): return self.lon


    def set_longitude(self, lon=0.0):
        # check bounds
        self.lon=lon
    
    
    def set_latitude_longitude(self, lat, lon):
        self.set_latitude(lat)
        self.set_longitude(lon)
        
        
    def get_latitude_longitude(self):
        return (self.lat, self.lon)
    
    
    def get_formatted_latitude(self):
        return "%.3f" % self.lat


    def get_formatted_longitude(self):
        return "%.3f" % self.lon

                
    def get_formatted_latitude_longitude(self):
        return (self.get_formatted_latitude(), self.get_formatted_longitude())
        
         
    def get_locator(self) :
        return self.get_locator_from_latlon(self.lat, self.lon)
        
        
    def set_locator(self, locator=''):
        #check it's valid
        self.locator=locator
        self.lat, self.lon = self.get_latlon_from_locator(locator) 
        
    #
    # Internal methods follow.
    #
    
    # This function is a port from Marco Bersani's loccalc.c
    def get_latlon_from_locator(self, locator):
        # todo check the length and if its a valid format
        locator = locator.upper()
        lon = -180.0 + self.ucase_letters.index(locator[0]) * 20.0 +\
                float(locator[2]) * 2.0 +\
                (self.ucase_letters.index(locator[4])+0.5) / 12.0;

        lat = -90.0 + self.ucase_letters.index(locator[1]) * 10 +\
                float(locator[3]) +\
                (self.ucase_letters.index(locator[5])+0.5) / 24;
    
        return (lat, lon);

    
    # This function is a port from Marco Bersani's loccalc.c
    def get_locator_from_latlon(self, lat=0.0, lon=0.0):
        lo = (lon+180.0)/20.0
        la = (lat+90.0)/10.0

        alo = math.floor(lo)
        bla = math.floor(la)
        lo = (lo-alo)*10.0
        la = (la-bla)*10.0

        clo = math.floor(lo)
        dla = math.floor(la)

        elo = math.floor((lo-clo)*24.0)
        fla = math.floor((la-dla)*24.0)

        return self.ucase_letters[int(alo)] +\
                        self.ucase_letters[int(bla)] +\
                        "%d" % clo +\
                        "%d" % dla +\
                        self.lcase_letters[int(elo)] +\
                        self.lcase_letters[int(fla)]

    # Accepts a HamLocation as the single arguement
    # Returns a tuple (bearing, distance)
    # Default unit is kilometres
    def path_to(self, target_location, unit=UNIT_KM ):

#/* ------Subroutine--------------------
#        Calculate beam heading and distance
#   Input : lon1  = Longitude 1 in degrees.
#         : lat1  = Latitude 1 in degrees.
#         : lon2  = Longitude 2 in degrees.
#         : lat2  = Latitude 2 in degrees.
#   Output: cb   = Beam heading in degrees.
#           di   = Distance in kilometers.
#           dmi  = Distance in miles.
# ------------------------------------ */


        lo1=-self.lon * math.pi/180.0   # Convert degrees to radians
        la1=self.lat * math.pi/180.0
        lo2=-target_location.get_longitude() * math.pi/180.0
        la2=target_location.get_latitude() * math.pi/180.0

        # Get local earth radius
        radius=self.local_earth_radius(self.lat)

        # Calculates distance in km and in miles
        di = math.acos(math.cos(la1)*math.cos(lo1)*math.cos(la2)*math.cos(lo2)+math.cos(la1)*math.sin(lo1)*math.cos(la2)*math.sin(lo2)+math.sin(la1)*math.sin(la2))*radius

        if (unit == self.UNIT_MILES):
            di = di/1.609

        # Calculates beam heading
        x=math.atan2(math.sin(lo1-lo2)*math.cos(la2),math.cos(la1)*math.sin(la2)-math.sin(la1)*math.cos(la2)*math.cos(lo1-lo2))/math.pi*180;

        if(x<0):
            cb=x+360
        else:
            cb=x
        return(cb, di)


    #-------------- Subroutine -----------------------
   #Calculate local earth radius from latitude
   #Input : lat = Latitude in decimal degrees (+ = North; - = South)
   #Output: earth radius (km)
   #------------------------------------------------- 

    def local_earth_radius(self, lat):

        #Hayford axes (1909)
        a=6378.388                    # earth major axis (km) (equatorial axis) 
        b=6356.912                     # earth minor axis (km) (polar axis)
        esq=(a*a-b*b)/(a*a)        #calculates eccentricity^2 

        la=lat*math.pi/180.0     # convert latitude in radians 
        sla=math.sin(la)                    # calculates sinus of latitude 
        r=a*math.sqrt(1-esq)/(1-esq*sla*sla);  #calculates local radius (km)
        return r
