#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# File: voafile.py
#
# Copyright (c) 2007 J.Watson
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

#from __future__ import with_statement
import codecs
import sys
import string
import math
import os.path
from hamlocation import *
from voaAreaRect import *
import calendar as cal

DEBUG = False

PROJECTION= {0:'aeqd', 1:'cyl'}

class VOAFile:
    """Encapsulates a VOACAP area calculation input (.voa) file.

    A typical .voa file is structured as follows;

    Model    :VOACAP
    Colors   :Black    :Blue     :Ignore   :Ignore   :Red      :Black with shading
    Cities   :Receive.cty
    Nparms   :    4
    Parameter:MUF      0
    Parameter:DBU      0
    Parameter:SNRxx    0
    Parameter:REL      0
    Transmit : 24.63N    46.72E   RIYADH (AR RIYAD)    Short
    Pcenter  : 24.63N    46.72E   RIYADH (AR RIYAD)
    Area     :    -180.0     180.0     -90.0      90.0
    Gridsize :  399    1
    Method   :   30
    Coeffs   :CCIR
    Months   :   5.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00   0.00
    Ssns     :     15      0      0      0      0      0      0      0      0
    Hours    :     12      0      0      0      0      0      0      0      0
    Freqs    :  9.850  0.000  0.000  0.000  0.000  0.000  0.000  0.000  0.000
    System   :  145     0.100   90   73     3.000     0.100
    Fprob    : 1.00 1.00 1.00 0.00
    Rec Ants :[default /swwhip.voa  ]  gain=   0.0   0.0
    Tx Ants  :[default /const17.voa ]  0.000  57.0   500.0000
        
    """
    def __init__(self, fn):
        self.TX_SITE     = 100
        self.P_CENTRE    = 101
        self.RX_SITE     = 102

        self.gridsize = 0
        self.pcentrelabel = ''
        self.pcentrelat = 0.0
        self.pcentrelon = 0.0
        self.txlabel = u''
        self.txlat = 0.0
        self.txlon = 0.0
        self.txPower = 0.0
        self.txBearing = 0.0
        self.txAntenna = ''
        self.rxAntenna = ''
        self.txGain = 0.0
        self.projection = 0
        self.llcrnrlon = 0.0
        self.llcrnrlat = 0.0
        self.urcrnrlon = 0.0
        self.urcrnrlat = 0.0
        self.monthDays = []
        self.ssns = []
        self.utcs = []
        self.frequencies = []

        self.XNOISE = 145
        self.AMIND = 0.100
        self.XLUFP = 90
        self.RSN = 16
        self.PMP = 3.000
        self.DMPX = 0.100 

        self.PSC1 = 1.0
        self.PSC2 = 1.0
        self.PSC3 = 1.0
        self.PSC4 = 1.0
        
        self.filename = fn
        
    def parse_file(self):
        voaFile = codecs.open(self.filename, "r", "utf-8")
        try:
            #voaFile = open(self.filename)
            for line in voaFile:
                if line.startswith("Area"):
                    self.llcrnrlon = float(line[11:20])
                    self.llcrnrlat = float(line[31:40])
                    self.urcrnrlon = float(line[21:30])
                    self.urcrnrlat = float(line[41:50])
                    if DEBUG: print self.llcrnrlon, self.llcrnrlat, self.urcrnrlon, self.urcrnrlat
                elif line.startswith("Gridsize"):
                    self.gridsize = int(line[11:16])
                    if DEBUG: print "Gridsize = ", self.gridsize
                    if PROJECTION.has_key(int(line[19:20])):
                        self.projection = PROJECTION[int(line[19:20])]
                    if DEBUG: print "Projection = ", self.projection                
                elif line.startswith("Pcenter"):
                    self.pcentrelabel = line[27:47].strip()
                    if DEBUG: print "PCentre = ", self.pcentrelabel
                    self.pcentrelat = self.parse_lat_lon(line[11:20])                     
                    if DEBUG: print "PCentre Lat = ", self.pcentrelat
                    self.pcentrelon = self.parse_lat_lon(line[21:30])
                    if DEBUG: print "PCentre Lon = ", self.pcentrelon
                elif line.startswith("System"):
                    self.XNOISE = int(line[11:15].strip())
                    self.AMIND = float(line[16:25].strip())
                    self.XLUFP = int(line[26:30].strip())
                    self.RSN = int(line[31:35].strip())
                    self.PMP = float(line[36:45].strip())
                    self.DMPX = float(line[46:55].strip())    
                elif line.startswith("Fprob"):
                    self.PSC1 = float(line[11:15].strip())
                    self.PSC2 = float(line[11:15].strip())
                    self.PSC3 = float(line[11:15].strip())
                    self.PSC4 = float(line[11:15].strip())                                        
                elif line.startswith("Transmit"):
                    self.txlabel = line[30:50].strip()
                    if DEBUG: print "Tx. = ", self.txlabel
                    self.txlat = self.parse_lat_lon(line[10:20])
                    if DEBUG: print self.txlat
                    self.txlon = self.parse_lat_lon(line[20:30])
                    if DEBUG: print self.txlon
                elif line.startswith("Tx Ants"):
                    self.txPower = float(line[49:60].strip())
                    self.txBearing = float(line[40:46].strip())
                    self.txGain = float(line[33:39].strip())
                    self.txAntenna = self.strcompress(line[10:33].strip())
                elif line.startswith("Rec Ants"):
                    self.rxAntenna = self.strcompress(line[10:33].strip())
                elif line.startswith("Hours    :"):
                    self.utcs = []
                    file_times = string.split(line[10:len(line)])
                    for time in file_times:
                        self.utcs.append(int(time))
                elif line.startswith("Ssns     :"):
                    self.ssns = []
                    file_ssns = string.split(line[10:len(line)])
                    for ssn in file_ssns:
                        self.ssns.append(int(ssn))
                elif line.startswith("Months   :"):
                    self.monthDays = []
                    file_months = string.split(line[10:len(line)])
                    for month in file_months:
                        self.monthDays.append(float(month))
                elif line.startswith("Freqs    :"):
                    self.frequencies = []
                    file_freqs = string.split(line[10:len(line)])
                    for freq in file_freqs:
                        self.frequencies.append(float(freq))
                        
# The following lines were originally commented out to get the script to 
# run correctly on python 2.4.  They have been uncommented now that python
# 2.5 is more widely used.
        except IOError:
            print "Error opening/reading file ", fn
            sys.exit(1)
        finally:
            if DEBUG: print "Closing the file"
            voaFile.close()
            
    def get_gridsize(self):    return self.gridsize
    def set_gridsize(self, gridsize):
        self.gridsize = int(gridsize)

    def get_centre_label(self): return self.pcentrelabel
    def get_centre_lat(self):    return self.pcentrelat
    def get_centre_lon(self):    return self.pcentrelon
    def get_tx_label(self): return self.txlabel
    def get_tx_lat(self): return self.txlat
    def get_tx_lon(self): return self.txlon


    def get_location(self, location):
        """Returns a HamLocation defining a location associated with the plot.  
        
        Keyword arguments
        location -- specifies the location to return.  Valid values are
        VOAFile.TX_SITE, VOAFile.RX_SITE or VOAFile.P_CENTRE.
        
        """ 
        if location == self.TX_SITE:    
            return HamLocation(self.txlat, self.txlon, self.txlabel)
        elif location == self.P_CENTRE:
            return HamLocation(self.pcentrelat, self.pcentrelon, self.pcentrelabel)
        elif location == self.RX_SITE:
            return HamLocation(self.rxlat, self.rxlon, self.rxlabel)

    
    def set_location(self, location, label, lon, lat):
        """Sets one of the locations associated with the plot.
        
        Keyword arguments
        location -- specifies the loation to set.  Valid value is 
        VOAFile.TX_SITE (This is the only type currently supported)
        """
        if location == self.TX_SITE:    
            self.txlabel = label
            self.txlon = float(lon)
            self.txlat = float(lat)

    def get_projection(self): return self.projection
    
    def get_num_plots(self):
        try:
            num_plots = self.monthDays.index(0.0)
        except (ValueError):
            num_plots = len(self.monthDays)
        if DEBUG: print "number of plots = ", num_plots
        return num_plots


    def get_monthday(self, field):
        """Returns the month.day for the specified field, e.g 20th December
        is represented by the month day (float) value '12.20'.  
        
        Keyword arguments
        field -- an integer specifying the field to return.  Valid values are 
        in the range 0-11.        
        
        """
        return self.monthDays[int(field)]


    def get_month(self, field):
        """Returns an integer representing the month for the specified field.
        
        Keyword arguments
        field -- an integer specifying the field to return.  Valid values are 
        in the range 0-11.
        
        """        
        return int(math.floor(self.monthDays[int(field)]))


    def get_day(self, field):
        """Returns an integer representing the day for the specified field.
        
        Keyword arguments
        field -- an integer specifying the field to return.  Valid values are 
        in the range 0-11.
        
        """        
        x, y = math.modf(self.monthDays[int(field)])
        return int(x * 10)

    def clear_plot_data(self):
        self.utcs = []
        self.ssns = []
        self.monthDays = []
        self.frequencies = []

    def add_plot(self, plot_parameters):
        """This method replaces the earlier 'set' type methods.
        Keyword Arguments
        plot_parameters -- a (freq, utc, month_day, ssn) tuple representing
        the plot parameters.
        """
        freq, utc, md, ssn = plot_parameters
        self.utcs.append(int(utc))
        self.ssns.append(round(float(ssn)))
        self.monthDays.append(float(md))
        self.frequencies.append(float(freq))
        

    def get_utc(self, field):
        """Returns the time (UTC) for a specified field.
        
        Keyword arguments
        field -- an integer specifying the field to return.  Valid values are 
        in the range 0-11.    
        
        """         
        return self.utcs[int(field)]
         

    def set_rx_antenna(self, data_file, gain=0.0, bearing=0.0):
        self.rx_ant_data_file = data_file
        self.rx_ant_gain = gain
        self.rx_ant_bearing = bearing


    def set_tx_antenna(self, data_file, design_freq=0.0, bearing=0.0, power=0.125):
        self.tx_ant_data_file = data_file
        self.tx_ant_design_freq = design_freq
        self.tx_ant_bearing = bearing
        self.tx_ant_power = power


    def set_xnoise(self, xnoise):
        self.XNOISE = int(xnoise)

    def set_amind(self, amind):
        self.AMIND = float(amind)
        
    def set_xlufp(self, xlufp):
        self.XLUFP = int(xlufp)
        
    def set_rsn(self, rsn):
        self.RSN = int(rsn)
        
    def set_pmp(self, pmp):
        self.PMP = float(pmp)
        
    def set_dmpx(self, dmpx):
        self.DMPX = float(dmpx)
        
    def set_psc1(self, psc1):
        self.PSC1 = float(psc1)
        
    def set_psc2(self, psc2):
        self.PSC2 = float(psc2)        

    def set_psc3(self, psc3):
        self.PSC3 = float(psc3)

    def set_psc4(self, psc4):
        self.PSC4 = float(psc4)

    def set_area(self, area):
        _lat, _lon = area.get_sw()
        self.set_ll_corner_lat(_lat)
        self.set_ll_corner_lon(_lon)
        _lat, _lon = area.get_ne()
        self.set_ur_corner_lat(_lat)
        self.set_ur_corner_lon(_lon)
        
    def get_area_rect(self):
        return VOAAreaRect(self.llcrnrlat, self.llcrnrlon, self.urcrnrlat, self.urcrnrlon)

    def get_ll_corner_lon(self): return self.llcrnrlon
    def set_ll_corner_lon(self, lon): self.llcrnrlon = float(lon)
    
    def get_ll_corner_lat(self): return self.llcrnrlat
    def set_ll_corner_lat(self, lat): self.llcrnrlat = float(lat)
    
    def get_ur_corner_lon(self): return self.urcrnrlon 
    def set_ur_corner_lon(self, lon): self.urcrnrlon = float(lon)
    
    def get_ur_corner_lat(self): return self.urcrnrlat
    def set_ur_corner_lat(self, lat): self.urcrnrlat = float(lat)
    

    def get_minimal_plot_description_string(self,field, plot_type, time_zone=0):
        """Returns a formatted string that may be used as a title for the plot.
        
        Keyword arguments
        field -- an integer specifying the field to return.  Valid values are 
        in the range 0-11. 
        plot_type -- a string specifying the plot type.  Valid values are 
        'MUF', 'REL' and 'SNR'
        time_zone -- an integer specifying the time zone.  Default = 0
        
        """
        _month = cal.month_abbr[int(math.floor(self.monthDays[int(field)]))]
        hour = int(self.utcs[int(field)] + time_zone)
        #todo can't we do this with a proper python time class????
        if hour > 24: 
            hour = hour - 24
        elif hour < 0: 
            hour = hour + 24

        if (time_zone == 0):
            hour_str = "%02d00 UTC" % (hour)
        else:
            _sign = '+' if (time_zone >= 0) else ''
            hour_str = "%02d00 UTC%s%s : " % (hour, _sign, time_zone)
        theSSN = str(self.ssns[int(field)])

        
        if (plot_type == 'MUF'):
            return _month + ', ' + hour_str
            #return hour_str + _month+ ' : SSN ' + theSSN + ' : ' +thePower
        else:
            # Add the frequency to the data string
            theFrequency = "%.3f MHz" % self.frequencies[int(field)]
            return _month + ', ' + hour_str + ', ' + theFrequency  
        
    # The following method is failing for Jari
    def get_plot_description_string(self, field, plot_type, time_zone=0):
        """Returns a formatted string that may be used as a title for the plot.
        
        Keyword arguments
        field -- an integer specifying the field to return.  Valid values are 
        in the range 0-11. 
        plot_type -- a string specifying the plot type.  Valid values are 
        'MUF', 'REL' and 'SNR'
        time_zone -- an integer specifying the time zone.  Default = 0
        
        """
        
        _month = cal.month_abbr[int(math.floor(self.monthDays[int(field)]))]
        hour = int(self.utcs[int(field)] + time_zone)
        #todo can't we do this with a proper python time class????
        if hour > 24: 
            hour = hour - 24
        elif hour < 0: 
            hour = hour + 24

        if (time_zone == 0):
            hour_str = "%02d00 UTC" % (hour)
        else:
            _sign = '+' if (time_zone >= 0) else ''
            hour_str = "%02d00 UTC%s%s : " % (hour, _sign, time_zone)
        theSSN = str(self.ssns[int(field)])

        theLat = self.lat_as_string(self.txlat) # "%.2f" % (self.txlat)
        theLon = self.lon_as_string(self.txlon) # "%.2f" % (self.txlon)
        siteLocation = self.txlabel + ' (' + theLat + ', ' + theLon + '), '

        if (self.txPower >= 1.0):
            thePower = "%.2f kW" % (self.txPower)
        else:
            thePower = "%.0f W" % ((self.txPower)*1000)


        ## some output stuff below to put on top of the coverage map --jpe
    	if self.RSN == 24:
    		theMode = "CW"
    	elif self.RSN == 38:
    		theMode = "SSB"
    	elif self.RSN == 49:
    		theMode = "AM"
    	elif self.RSN == 17:
    		theMode = "ROS"
    	else: theMode = str(self.RSN) # "N/A"
    	
    	print "****************************************"
        print "encoding: " + sys.getdefaultencoding()
        print "siteLocation:" + type(siteLocation).__name__
        print "_month:" + type(_month).__name__        
        print "hour_str:" + type(hour_str).__name__        

        print "thePower:" + type(thePower).__name__        
        print "theSSN:" + type(theSSN).__name__        
        print "theMode:" + type(theMode).__name__      


        if (plot_type == 'MUF'):
            return siteLocation + _month + ', ' + hour_str + ', ' + thePower + ', SSN ' + theSSN  
            #return hour_str + _month+ ' : SSN ' + theSSN + ' : ' +thePower
        else:
            # Add the frequency to the data string
            theFrequency = "%.3f MHz" % self.frequencies[int(field)]
            print "theFrequency:" + type(theFrequency).__name__    
            site_description = siteLocation + \
                    unicode(_month, "utf-8") + u', ' + \
                    unicode(hour_str, "utf-8") + u', ' + \
                    unicode(theFrequency, "utf-8") + u', ' + \
                    unicode(thePower, "utf-8") + \
                    u', SSN ' + unicode(theSSN, "utf-8") + \
                    u', Mode: ' + unicode(theMode, "utf-8")
            print "site_description:" + type(site_description).__name__   
            print "****************************************"
            return site_description    
        

    def get_detailed_plot_description_string(self, field):
        """Returns a string of comprehensive information about the plot.
        
        Keyword arguments
        field -- an integer specifying the field to return.  Valid values are 
        in the range 0-11. 
        
        """
#siteLocation = self.txlabel + ' : (Lon:' +    theLon + '$^\circ$, Lat:' + theLat + '$^\circ$)'
#        theLat = self.lat_as_string(self.txlat) # "%.2f" % (self.txlat)
#        theLon = self.lon_as_string(self.txlon) # "%.2f" % (self.txlon)
#        siteLocation = 'TX: ' + self.txlabel + ' (' + theLat + ', ' + theLon + ')'
        emmisionData = 'TX Ant: ' + self.txAntenna + ', RX Ants: ' + self.rxAntenna
#        emmisionData = 'Tx. Ant.: ' + self.txAntenna + \
#                            " : %.2f$^\circ$" % (self.txBearing) + \
#                            " : %.2f dBi" % (self.txGain)

        return emmisionData
#- Frequency
#- Grid Size

    
    def write_file(self):
        #f = open(self.filename, 'wt')
        f = codecs.open(self.filename, "wt", "utf-8")
        f.write('Model    :VOACAP\n')
        f.write('Colors   :Black    :Blue     :Ignore   :Ignore   :Red      :Black with shading\n')
        f.write('Cities   :Receive.cty\n')
        f.write('Nparms   :    4\n')
        f.write('Parameter:MUF      0\n')
        f.write('Parameter:DBU      0\n')
        f.write('Parameter:SNRxx    0\n')
        f.write('Parameter:REL      0\n')
        tmpStr= "Transmit :%10s%10s%18sShort\n" % (self.lat_as_string(self.txlat), self.lon_as_string(self.txlon), unicode(self.txlabel, "utf-8"))
        f.write(tmpStr)

        tmpStr= "Area     :%10.1f%10.1f%10.1f%10.1f\n" % \
                (self.llcrnrlon, self.urcrnrlon, self.llcrnrlat, self.urcrnrlat)  
        f.write(tmpStr)    

        tmpStr = "Gridsize :  %3d    1\n" % (self.gridsize)
        f.write(tmpStr)
        f.write('Method   :   30\n')
        f.write('Coeffs   :CCIR\n')
        
        tmpStr = "Months   :"
        for md in self.monthDays:
            tmpStr = tmpStr + "%7.2f" % md
        f.write(tmpStr+"\n")

        tmpStr = "Ssns     :"
        for ssn in self.ssns:
            tmpStr = tmpStr + "%7d" % ssn
        f.write(tmpStr+"\n")                

        tmpStr = "Hours    :"
        for utc in self.utcs:
            tmpStr = tmpStr + "%7d" % utc
        f.write(tmpStr+"\n")
        
        tmpStr = "Freqs    :"
        for freq in self.frequencies:
            tmpStr = tmpStr + "%7.3f" % freq
        f.write(tmpStr+"\n")

        tmpStr= "System   :%5d%10.3f%5d%5d%10.3f%10.3f\n" % \
                (self.XNOISE, self.AMIND, self.XLUFP, self.RSN, self.PMP, self.DMPX)
        f.write(tmpStr)        
                     
        tmpStr ="Fprob    :%5.2f%5.2f%5.2f%5.2f\n" % (self.PSC1, self.PSC2, self.PSC3, self.PSC4)
        f.write(tmpStr)
        tmpStr = "Rec Ants :[%21s]  gain=%6.1f%6.1f\n" % \
            (self.rx_ant_data_file, self.rx_ant_gain, self.rx_ant_bearing)
        f.write(tmpStr)
        tmpStr = "Tx Ants  :[%21s]%7.3f%6.1f%10.4f\n" % \
            (self.tx_ant_data_file, self.tx_ant_design_freq, self.tx_ant_bearing, self.tx_ant_power)
        f.write(tmpStr)    
        f.close()

    def parse_lat_lon(self, l_str):
        l = 0.0
        if DEBUG: print "l_str = ", l_str
        l_str = l_str.strip()
        if ((l_str.endswith('S')) or (l_str.endswith('W'))):
            l = 0 - float(l_str[:-1])
        else:
            l = float(l_str[:-1])                     
        if DEBUG: print "Lat/Lon = ", l
        return l
    
    def get_description(self):
        voa_str = "Filename           : %s \n" % (self.filename)
        voa_str = "%sGrid Size          : %d \n" % (voa_str, self.gridsize)
        voa_str = "%sPlot Centre        : %s (%.2f, %.2f) \n" % (voa_str, self.pcentrelabel, \
            self.pcentrelon, self.pcentrelat)
        voa_str = "%sTx. Site           : %s (%.2f, %.2f) \n" % (voa_str, self.txlabel, \
            self.txlon, self.txlat)
        voa_str = "%sLower Left Corner  : Lat.%.2f, Lon.%.2f \n" % (voa_str, self.llcrnrlat, self.llcrnrlon)
        voa_str = "%sUpper Right Corner : Lat.%.2f, Lon.%.2f \n" % (voa_str, self.urcrnrlat, self.urcrnrlon)
        return voa_str
        
    def lat_as_string(self, lat):
        if lat > 90.0 : lat = 90.0
        if lat < -90.0 : lat = -90.0
        lat_sign = 'N'
        if lat < 0.0:
            lat_sign = 'S'
        return "%5.2f%s" % (abs(lat), lat_sign)        
        
    def lon_as_string(self, lon):
        if lon > 180.0 : lon = 180.0
        if lon < -180.0 : lon = -180.0
        lon_sign = 'E'
        if lon < 0.0:
            lon_sign = 'W'
        return "%6.2f%s" % (abs(lon), lon_sign)
        
    # http://mail.python.org/pipermail/tutor/2007-October/057571.html
    def strcompress(self, mystring):
    	mystring_compressed = ''.join(mystring.split())
    	return mystring_compressed
