#!/usr/bin/env python
#
# File: voacapDefaults
# Version: 10Jul09
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

# A dictioanary poulated with the defaults for voacap

class VOADefaultDictionary(dict):

    def __init__(self, default=None):
        dict.__init__(self)
        self['foe'] = '1.0'
        self['fof1'] = '1.0'
        self['fof2'] = '1.0'
        self['foes'] = '0.0'
        self['mm_noise'] = '-145'
        self['min_toa'] = '3.0'
        self['required_reliability'] = '90'
        self['required_snr'] = '47'
        self['mpath'] = '3.0'
        self['delay'] = '0.1'
        self['model'] = '0'
        self['path'] = '0'
        self['tx_bearing'] = '0.0'
        self['tx_power'] = '100.0'
        self['rx_bearing'] = '0.0'        
        
        


    
