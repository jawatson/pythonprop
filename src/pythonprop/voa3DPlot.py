#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""A short script to display the contents of voacapg.out type files
in a 3D format. 

"""
# File: voa3DPlot.py
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
# 
#

import sys
import math

import matplotlib
#matplotlib.use('GTK3Agg')

from mpl_toolkits.mplot3d import Axes3D

from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg
import matplotlib.backends.backend_gtk3agg as gtkagg
from matplotlib.figure import Figure

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GObject
except  ImportError:
    pass
try:
    from gi.repository import Gtk
except  ImportError:
    sys.exit(1)

#import matplotlib.pyplot as plt

from optparse import OptionParser
import numpy as np
#import pylab as P

from .voaOutFile import VOAOutFile
from .voaPlotWindow import VOAPlotWindow

class VOA3DPlot:
    """Program to plot .out files produced by voacap in 3D"""
    
    AUTOSCALE = -1.0
    
    IMG_TYPE_DICT  = { 0:{'title':'', \
                            'min':0, \
                            'max':1, \
                            'y_labels':(0), \
                            'formatter':'defaultFormat'}, \
            1:{'title':'MUF Days (%)', \
                'min':0, \
                'max':1, \
                'y_labels':(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1),\
                'formatter':'percent_format'}, \
            2:{'title':'Circuit Reliability (%)', \
                'min':0, \
                'max':1, \
                'y_labels':(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1),\
                'formatter':'percent_format'}, \
            3:{'title':'SNR at Receiver (dB)', \
                'min':20, \
                'max':70, \
                'y_labels':(20, 30, 40, 50, 60, 70), \
                'formatter':'SNR_format'}, \
            4:{'title':'Signal Strength at Receiver (dBW)', \
                'min':-151, \
                'max':-43, \
                'y_labels':(-151, -145, -139, -133, -127, -121,-115, -109, \
                    -103, -93, -83, -73, -63, -53, -43), \
                'formatter':'SDBW_format'} }
    
    mono_font = {'family' : 'monospace'}
    #default_font = {'family' : 'sans-serif'}
      
    def __init__(self, data_file, 
                data_type = 2,
                color_map = 'jet',
                plot_label = "",
                time_zone = 0, 
                plot_max_freq = 30.0,
                run_quietly = False,
                save_file = '',
                parent = None):

        self.data_type = data_type
        self.data_file = VOAOutFile(data_file, \
                        time_zone=time_zone, \
                        data_type=self.data_type)

        self.image_defs = self.IMG_TYPE_DICT[self.data_type]
        
        #color_map = eval('P.cm.' + color_map)
    
        num_grp = self.data_file.get_number_of_groups()
        if num_grp < 2:
            md = Gtk.MessageDialog(parent, \
                Gtk.DialogFlags.MODAL,\
                Gtk.MessageType.ERROR, \
                Gtk.ButtonsType.CANCEL, \
                "There must be 2 groups or more")
            md.run()
            md.destroy()
            return
        plot_groups = list(range(0, num_grp))

        self.subplots = []
        number_of_subplots = len(plot_groups)
        
        matplotlib.rcParams['axes.edgecolor'] = 'gray'
        matplotlib.rcParams['axes.facecolor'] = 'white'
        matplotlib.rcParams['axes.grid'] = True
        matplotlib.rcParams['figure.facecolor'] = 'white'
        matplotlib.rcParams['legend.fancybox'] = True
        matplotlib.rcParams['legend.shadow'] = True
        matplotlib.rcParams['figure.subplot.hspace'] = 0.45
        matplotlib.rcParams['figure.subplot.wspace'] = 0.35
        matplotlib.rcParams['figure.subplot.right'] = 0.85
        colorbar_fontsize = 12
               
        self.main_title_fontsize = 24
        matplotlib.rcParams['legend.fontsize'] = 12
        matplotlib.rcParams['axes.labelsize'] = 12
        matplotlib.rcParams['axes.titlesize'] = 10
        matplotlib.rcParams['xtick.labelsize'] = 10
        matplotlib.rcParams['ytick.labelsize'] = 10
        self.x_axes_ticks = np.arange(0, 25, 2)

        self.fig = Figure()
        ax = Axes3D(self.fig)
        
        X = np.arange(0, 25)
        Y = np.arange(0, len(plot_groups))
        X, Y = np.meshgrid(X, Y)

        data_buffer = [] # hold the Z data sets


        for chan_grp in plot_groups:
            (group_name, group_info, fot, muf, hpf, image_buffer) = \
                self.data_file.get_group_data(chan_grp)
            # Copy the element at [0] to the tail of the array 
            #to 'wrap-around' the values at 24hrs.
            np.resize(muf, len(muf)+1)
            muf[-1] = muf[0]
            data_buffer.append(muf)

        Z = np.vstack((tuple(data_buffer)))

	# set up the titles and labels
        ax.set_xticks(np.arange(0, 25, 2))

        if (plot_max_freq==self.AUTOSCALE) :
            z_max = math.ceil(max(muf) / 5.0) * 5.0
            z_max = min(plot_max_freq, 30.0)
            z_max = max(plot_max_freq, 5.0)
        else :
            z_max = math.ceil(plot_max_freq / 5.0) * 5.0
        z_ticks = [2, 5]
        for z_tick_value in np.arange(10, z_max+1, 5):
            z_ticks.append(z_tick_value) 
        #ax.set_yticks(z_ticks)

	#label axes
        tz_sign = '+' if (time_zone >= 0) else ''
        self.x_label = ax.set_xlabel('Time (UTC%s%s)' % (tz_sign, time_zone))
        self.y_label = ax.set_ylabel('Group')
        self.z_label = ax.set_zlabel('Frequency (MHz)')

	#do the plot
        ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=color_map)
        canvas = FigureCanvasGTK3Agg(self.fig)
        canvas.show()
        Axes3D.mouse_init(ax)
        VOAPlotWindow('pythonProp - ' + self.image_defs['title'], \
                        canvas, \
                        parent)
        return



def main(data_file):
    """Main entry point to the class when calling in standalone mode."""
    
    parser = OptionParser(usage="%voa3DPlot [options] file", \
                            version="%voaP2PPlot 0.8")

    #tested ok
    help_str = "Display a band plan indicated by the integer 1, 2 or 3 "
    help_str += "(e.g. 1:SWL 2:UK AMATEUR BANDS 3:KSA AMATEUR BANDS)"

    parser.add_option("-b", "--band", 
        dest = "plot_bands",
        choices = ['1', '2', '3'],
        help = help_str)

    parser.add_option("-f", "--freqmax", 
        dest = "y_max", 
        default = '30.0',
        help="Maximum frequency for the Y axis")

    parser.add_option("-g", "--group", 
        dest="plotGroups", 
        default='1',
        help="Group(s) to plot. e.g '-g 1,3,5,6'. (default = 1)")
    
    parser.add_option("-l", "--label",
        dest = "plot_label",
        default = "",
        help = "A text label, printed in the main title block")
        
    help_str = "COLOURMAP - may be one of 'autumn', 'bone', 'cool', 'copper',"
    help_str += "', 'hot', 'hsv', 'jet', 'pink', 'spring', 'summer', 'winter'."
    help_str += "Default = 'jet'"
    parser.add_option("-m", "--cmap", 
        dest="color_map", 
        default='jet',
        choices = [ 'autumn', 'bone', 'cool', 'copper', 'gray', \
                'hot', 'hsv', 'jet', 'pink', 'spring','summer', 'winter' ],
        help=help_str)

    parser.add_option("-o", "--outfile", 
        dest="save_file",
        help="Save to FILE.", metavar="FILE")

    parser.add_option("-q", "--quiet",
        dest="run_quietly",
        action="store_true",  
        default=False,
        help="Process quietly (don't display plot on the screen)")    

    parser.add_option("-t", "--datatype", 
        dest="data_type", 
        default=1,
        help="Image type 0:None 1:MUFday 2:REL 3:SNR 4:S DBW (default = 1)")    

    parser.add_option("-z", "--timezone", 
        dest="time_zone", 
        default=0,
        help="Time zone (integer, default = 0)")
        
    (options, args) = parser.parse_args()
    
    if options.data_type:
        if int(options.data_type) not in VOA3DPlot.IMG_TYPE_DICT:
            print("Unrecognised plot type: Defaulting to MUF days")
            options.data_type = 1
            
    
    if options.y_max:
        if options.y_max == 'a':
            plot_max_freq = VOA3DPlot.AUTOSCALE
        else:
            try:    
                plot_max_freq = float(options.y_max)
            except TypeError:
                print("-f must be either 'a' or a float in the range 5.0 - 30.0")
                sys.exit(1)
            plot_max_freq = min(plot_max_freq, 30.0)
            plot_max_freq = max(plot_max_freq, 5.0)

    if options.time_zone:
        time_zone = int(options.time_zone)
        if time_zone > 12: 
            time_zone = 0
        if time_zone < -12: 
            time_zone = 0
    else:
        time_zone = 0

    if options.plotGroups:
        if options.plotGroups == 'a':
            plot_groups = ['a']
        else:
            try:
                if options.plotGroups.find(','):
                    plot_groups = options.plotGroups.split(',')
                else:
                    plot_groups = [int(options.plotGroups)]
                #convert to integers
                for i in range(0, len(plot_groups)):
                    try:
                        plot_groups[i] = int(plot_groups[i])-1
                    except:
                        plot_groups.pop(i)
                if len(plot_groups) == 0:
                    print("Error reading plot_groups, resetting to '1'")
                    plot_groups = [0]
                plot_groups.sort()
            except:
                print("Error reading groups, resetting to '1'")
                plot_groups = [1]


    VOA3DPlot(data_file, 
                    data_type = int(options.data_type), 
                    plot_label = options.plot_label,
                    color_map=options.color_map,
                    time_zone = time_zone,
                    plot_max_freq = plot_max_freq,
                    run_quietly = options.run_quietly,
                    save_file = options.save_file)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main(sys.argv[-1])
    else:
        print('voa3DPlot error: No data file specified')
        print('voa3DPlot [options] filename')
        sys.exit(1)

      

