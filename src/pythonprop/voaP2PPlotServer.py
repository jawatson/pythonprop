#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# File: voaP2PPlot.py
#
# Copyright (c) 2007 J.A.Watson
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
# A short script to display the contents of voacapg.out type files
# (method 30). 
#
# Examples
# './voaP2PPlot -c voacapx.out' plots the contents of the file 
# named voacapg.out.  Adds contours to the image overlay.
#
# './voaP2PPlot -c -t 2 voacapx.out' prints a REL overlay
#
# './voaP2PPlot -c -t 2 -m 11 voacapx.out' Uses colourmap 11 (Use -h 
# to list the available colour maps
#
# './voaP2PPlot -c -t 2 -o saveFile.png voacapx.out' save plot to 
# a file named saveFile.png
#
# './voaP2PPlot -h' - Prints a help message
#
# './voaP2PPlot.py -c -b 1 voacapx.out' overlay SW bands on the plot
#
# './voaP2PPlot.py -z 3 voacapx.out' Plots for a timezone of + 3 hours

import sys
import re
import os
import math
from optparse import OptionParser

import matplotlib
matplotlib.use('Agg')

from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.backends.backend_agg as agg
import matplotlib.transforms as mtransforms
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

from voaOutFile import *
from voaPlotWindow import *
#from voaMultiPlot import *

import pylab as P

import gettext
import locale
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
lang.install()


class VOAP2PPlot:
    """Program to plot .out files produced by voacap"""
    
    AUTOSCALE = -1.0
    
    IMG_TYPE_DICT  = { 0:{'title':'', 'min':0, 'max':1, 'y_labels':(0), 'formatter':'defaultFormat'}, \
        1:{'title':_('MUF Days (%)'), 'min':0, 'max':1, 'y_labels':(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 'formatter':'percent_format'}, \
        2:{'title':_('Circuit Reliability (%)'), 'min':0, 'max':1, 'y_labels':(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 'formatter':'percent_format'}, \
        3:{'title':_('SNR at Receiver (dB)'), 'min':20, 'max':70, 'y_labels':(20, 30, 40, 50, 60, 70), 'formatter':'SNR_format'}, \
        4:{'title':_('Signal Strength at Receiver (dBW)'), 'min':-151, 'max':-43, 'y_labels':(-151, -145, -139, -133, -127, -121,-115, -109, -103, -93, -83, -73, -63, -53, -43), 'formatter':'SDBW_format'} }
    
    mono_font = {'family' : 'monospace'}
    #default_font = {'family' : 'sans-serif'}

    S_LABELS = ['S1', 'S2', 'S3', 'S4', 'S5','S1', 'S2', 'S3', 'S4', 'S5','S1', 'S2', 'S3']

    UK_BANDS = [(3.5, 3.8), (7.0, 7.2), (10.1, 10.15), (14.0, 14.35), (18.068, 18.168), \
                    (21.0, 21.45), (24.8, 24.99), (28.0, 29.7)]
    SWL_BANDS = [(3.200, 3.400), (3.900, 4.000), (4.750, 5.060), \
                    (5.950, 6.200), (7.100, 7.300), (9.500, 9.900), (11.650, 12.050), \
                    (13.600, 13.800), (15.100, 15.600), (17.550, 17.900), \
                    (18.900, 19.020), (21.450, 21.850), (25.670, 26.100)]
    KSA_BANDS = [(7.0, 7.2), (14.0, 14.35), (18.068, 18.168), \
                    (21.0, 21.45), (24.89, 24.99), (28.0, 29.7)]

        
    def __init__(self, data_file, 
                plot_groups = [1], 
                data_type = 2,
                color_map = 'jet',
                plot_contours = False,
                plot_label = "",
                plot_bands = None,
                time_zone = 0, 
                plot_max_freq = 30.0,
                run_quietly = True,
                save_file = '',
                dpi=150,
                parent = None):

        self.data_type = data_type
        self.run_quietly = run_quietly
        self.dpi=dpi

        self.df = VOAOutFile(data_file, time_zone=time_zone, data_type=self.data_type, quiet=run_quietly)

        self.image_defs = self.IMG_TYPE_DICT[self.data_type]
        
        color_map = eval('P.cm.' + color_map)
    
        if plot_groups[0]=='a':            
            num_grp = self.df.get_number_of_groups()
            plot_groups = range(0,num_grp)

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
               
        if number_of_subplots <= 1:    
            self.num_rows = 1
            self.main_title_fontsize = 24
            matplotlib.rcParams['legend.fontsize'] = 12
            matplotlib.rcParams['axes.labelsize'] = 12
            matplotlib.rcParams['axes.titlesize'] = 8
            matplotlib.rcParams['xtick.labelsize'] = 10
            matplotlib.rcParams['ytick.labelsize'] = 10
            matplotlib.rcParams['figure.subplot.top'] = 0.79 # single figure plots have a larger title so require more space at the top.
            self.x_axes_ticks = P.arange(0,25,2)
        elif ((number_of_subplots >= 2) and (number_of_subplots <= 6 )):
            self.num_rows = 2
            self.main_title_fontsize = 18
            matplotlib.rcParams['legend.fontsize'] = 10
            matplotlib.rcParams['axes.labelsize'] = 10
            matplotlib.rcParams['axes.titlesize'] = 11
            matplotlib.rcParams['xtick.labelsize'] = 8
            matplotlib.rcParams['ytick.labelsize'] = 8
            self.x_axes_ticks = P.arange(0,25,4)
        else:
            self.num_rows = 3
            self.main_title_fontsize = 16
            matplotlib.rcParams['legend.fontsize'] = 8
            matplotlib.rcParams['axes.labelsize'] = 8
            matplotlib.rcParams['axes.titlesize'] = 10
            matplotlib.rcParams['xtick.labelsize'] = 6
            matplotlib.rcParams['ytick.labelsize'] = 6
            self.x_axes_ticks = P.arange(0,25,4)
        
        self.num_cols = int(math.ceil(float(number_of_subplots)/float(self.num_rows)))  
        self.fig=Figure(figsize=(7,6.5))
        self.main_title_label = self.fig.suptitle(plot_label+unicode(self.image_defs['title'],'utf-8'), fontsize=self.main_title_fontsize)

        for chan_grp in plot_groups:
            (group_name, group_info, fot, muf, hpf, image_buffer) = self.df.get_group_data(chan_grp)
            
            ax = self.fig.add_subplot(self.num_rows, 
                    self.num_cols, 
                    plot_groups.index(chan_grp)+1)
            
            self.subplots.append(ax)
            
            if number_of_subplots > 4:
                #save a little space by only labelling the outer edges of the plot
                ax.label_outer()
                        
            _sign = '+' if (time_zone >= 0) else ''
            self.x_label = ax.set_xlabel(_('Time (UTC%(sig)s%(tz)s)') % {'sig':_sign, 'tz':time_zone})
            self.y_label = ax.set_ylabel(_('Frequency (MHz)'))

            ## Autoscale y (frequency axis)
            if (plot_max_freq==self.AUTOSCALE) :
                y_max = math.ceil(max(muf) / 5.0) * 5.0
                y_max = min(plot_max_freq, 30.0)
                y_max = max(plot_max_freq, 5.0)
            else :
                y_max = math.ceil(plot_max_freq / 5.0) * 5.0
            #resize the image
            image_buffer = image_buffer[0:y_max-1,:]
            
            y_ticks = [2, 5]
            for y_tick_value in P.arange(10, y_max+1, 5):
                y_ticks.append(y_tick_value)   
 
            #The line below has been modified to omit plottinf the fot
            ax.plot(range(0, 25), muf,'r-')
            ax.set_ylim([2, y_max])

            ax.set_xticks(self.x_axes_ticks)
            ax.set_yticks(y_ticks)
            

            #self.add_legend(ax)
            title_str = group_info.strip()
            if number_of_subplots > 1:
                title_str = self.get_small_title(title_str)
            self.subplot_title_label = ax.set_title(title_str, multialignment='left', **self.mono_font)
            
            if (self.data_type > 0):
                im = ax.imshow(image_buffer, interpolation='bicubic', 
                    extent=(0, 24, 2, y_max), origin = 'lower', cmap=color_map,
                    alpha = 0.95,
                    norm = P.Normalize(clip = False, 
                    vmin=self.image_defs['min'], 
                    vmax=self.image_defs['max']))
                if plot_contours:
                    ax.contour(image_buffer, self.image_defs['y_labels'], extent=(0, 24, 2, y_max), linewidths=1.0, colors='k', alpha=0.6)
    
            if plot_bands:
                for a,b in plot_bands:
                    ax.axhspan(a, b, alpha=0.5, ec='k', fc='k')

        if (self.data_type > 0):
            self.cb_ax = self.fig.add_axes(self.get_cb_axes())
            self.fig.colorbar(im, cax=self.cb_ax, 
                    orientation='vertical',
                    format = P.FuncFormatter(eval('self.'+self.image_defs['formatter'])))
            for t in self.cb_ax.get_yticklabels():
                t.set_fontsize(colorbar_fontsize)

        canvas = FigureCanvasAgg(self.fig)
        self.fig.canvas.mpl_connect('draw_event', self.on_draw)
        #canvas.show()

        if save_file :
            self.save_plot(canvas, save_file)

        #if not self.run_quietly:
            # todo consider using a scrolled pane here...
            #dia = VOAPlotWindow('pythonProp - ' + self.image_defs['title'], canvas, parent, dpi=self.dpi)
        #return
    
    
    def on_draw(self, event):
        #print 'drawing'
        top = self.fig.subplotpars.top
        bottom = self.fig.subplotpars.bottom
        hspace = self.fig.subplotpars.hspace
        wspace = self.fig.subplotpars.wspace

        needs_adjusting = False
        
        # Calculate the area required at the top of the plot 
        # (Main title and subplot title)
        subplot_title_height = 0
        main_title_height = 0

        for subplot in self.subplots:
            if subplot.is_first_row():
                bbox = subplot.title.get_window_extent()
                transformed_bbox = bbox.inverse_transformed(self.fig.transFigure)
                subplot_title_height = max(transformed_bbox.height, subplot_title_height)
            
        #print 'title = ', self.fig.get_label()
        
        bbox = self.main_title_label.get_window_extent()
        main_title_height = bbox.inverse_transformed(self.fig.transFigure).height  
        
        preferred_top_space = 1.25*(subplot_title_height + main_title_height)

        if ((1 - top) < preferred_top_space) or (((1 - top) - preferred_top_space)>0.11):
            top = 0.99 - preferred_top_space
            needs_adjusting = True
         
        if needs_adjusting:  
            #print 'adjusting'
            #todo if the colorbar dosn't exist, ignore this.
            self.fig.subplots_adjust(top = top, bottom = bottom, hspace = hspace, wspace = wspace)
            self.cb_ax.set_position(self.get_cb_axes())  
            self.fig.canvas.draw()
            
        return False
        
    def add_legend(self, ax):
        leg = ax.legend(('MUF', 'FOT'),ncol=1)
        leg.get_frame().set_alpha(0.75)
        return leg
        
    def save_plot(self, canvas, filename=None):
        #canvas.print_figure(filename, dpi=150, facecolor='white', edgecolor='white')
        self.fig.savefig(filename, dpi=self.dpi, facecolor='white', edgecolor='white')

    def get_cb_axes(self):
        # an equivalent of get_tightbox would be really useful here...                
        #bbox = self.subplots[0].get_window_extent()
        bbox = self.subplots[0].get_yaxis().get_clip_box()
        axis_upper_y = bbox.inverse_transformed(self.fig.transFigure).ymax
        bbox = self.subplots[-1].get_window_extent()
        axis_lower_y = bbox.inverse_transformed(self.fig.transFigure).ymin
        return [0.9, axis_lower_y, 0.02, axis_upper_y-axis_lower_y]

    #def percentFormat(x, pos):
    #    'The two args are the value and tick position'
    #    return '%(percent)3d%% (%(days)d days)' % {'percent':x*100, 'days':x*30.0} 
    def percent_format(self, x, pos):
        return '%(percent)3d%%' % {'percent':x*100} 

    def SNR_format(self, x, pos):
        return '%3ddB' % x

    def defaultFormat(self, x, pos):
        return '%d' % x

    def SDBW_format(self, x, pos):
        S_DICT = {-151:'S1', -145:'S2', -139:'S3', -133:'S4', -127:'S5', \
                    -121:'S6', -115:'S7', -109:'S8', -103:'S9', -93:'S9+10dB', \
                    -83:'S9+20dB', -73:'S9+30dB', -63:'S9+40dB', -53:'S9+50dB', -43:'S9+60dB'}
        if S_DICT.has_key(x):
            return _('%(value)ddBW (%(s_value)s)') %{'value':x, 's_value':S_DICT[x]}
        else : return '%3d' % x

    def get_small_title(self, title_string):
    #Mar    2008          SSN =   7.                Minimum Angle= 3.000 degrees
   #RIYADH (AR RIYAD)   YORK                  AZIMUTHS          N. MI.      KM
   #24.63 N   46.71 E - 53.96 N    1.08 W    322.62  110.27    2753.7   5099.5
   #XMTR  2-30 2-D Table [default/swwhip.voa   ] Az=322.6 OFFaz=  0.0   0.005kW
   #RCVR  2-30 2-D Table [default/swwhip.voa   ] Az=110.3 OFFaz=360.0
   #3 MHz NOISE = -145.0 dBW     REQ. REL = 90%    REQ. SNR = 10.0 dB
        title_lines = title_string.split('\n')
        #Extract Month / year and SSN
        tmp_line = title_lines[0].split()
        tmp_str = tmp_line[0] + ' ' + tmp_line[1] + ' SSN:' + tmp_line[4].rstrip('.')
        return tmp_str


def main(data_file):
    parser = OptionParser(usage=_("%voaP2PPlot [options] file"), version="%voaP2PPlot 0.9")

    #tested ok
    parser.add_option("-b", "--band", 
        dest = "plot_bands",
        choices = ['1', '2', '3'],
        help = _("Display a band plan indicated by the integer 1, 2 or 3 (e.g. 1:SWL 2:UK AMATEUR BANDS 3:KSA AMATEUR BANDS)"))

    parser.add_option("-c", "--contour",
        dest="plot_contours", 
        default=False, 
        action="store_true",
        help=_("Print contour lines on the plot"))

    parser.add_option("-f", "--freqmax", 
        dest = "y_max", 
        default = '30.0',
        help=_("Maximum frequency for the Y axis"))

    parser.add_option("-g", "--group", 
        dest="plotGroups", 
        default='1',
        help=_("Group(s) to plot. e.g '-g 1,3,5,6'. (default = 1)"))
    
    parser.add_option("-l", "--label",
        dest = "plot_label",
        default = "",
        help = _("A text label, printed in the main title block"))
        
    parser.add_option("-m", "--cmap", 
        dest="color_map", 
        default='jet',
        choices = [ 'autumn', 'bone', 'cool', 'copper', 'gray', \
                'hot', 'hsv', 'jet', 'pink', 'spring','summer', 'winter' ],
        help=_("COLOURMAP - may be one of 'autumn', 'bone', 'cool', 'copper', 'gray', 'hot', 'hsv', 'jet', 'pink', 'spring', 'summer', 'winter'.  Default = 'jet'"))

    parser.add_option("-o", "--outfile", 
        dest="save_file",
        help="Save to FILE.", metavar="FILE")

    parser.add_option("-q", "--quiet",
        dest="run_quietly",
        action="store_true",  
        default=False,
        help=_("Process quietly (don't display plot on the screen)"))

    parser.add_option("-r", "--resolution",
        dest="dpi",
        default=150,
        help=_("Dots per inch (dpi) of saved file."))

    parser.add_option("-t", "--datatype", 
        dest="data_type", 
        default=1,
        help=_("Image type 0:None 1:MUFday 2:REL 3:SNR 4:S DBW (default = 1)"))


    parser.add_option("-z", "--timezone", 
        dest="time_zone", 
        default=0,
        help=_("Time zone (integer, default = 0)"))
        
    (options, args) = parser.parse_args()
    
    if options.data_type:
        if not VOAP2PPlot.IMG_TYPE_DICT.has_key(int(options.data_type)):
            print _("Unrecognised plot type: Defaulting to MUF days")
            options.data_type = 1
            
    if options.plot_bands:
        if int(options.plot_bands) == 1: bands = VOAP2PPlot.SWL_BANDS
        elif int(options.plot_bands) == 2: bands = VOAP2PPlot.UK_BANDS
        elif int(options.plot_bands) == 3: bands = VOAP2PPlot.KSA_BANDS
        else: bands = None
    else:
        bands = None

    if options.y_max:
        if options.y_max == 'a':
            plot_max_freq = VOAP2PPlot.AUTOSCALE
        else:
            try:    
                plot_max_freq = float(options.y_max)
            except:
                print _("-f arguments must be either 'a' or a decimal in the range 5.0 - 30.0")
                os._exit(1)
            plot_max_freq = min(plot_max_freq, 30.0)
            plot_max_freq = max(plot_max_freq, 5.0)

    if options.dpi:
        try:
            options.dpi=int(options.dpi)
        except:
            print "failed to read dpi"
            options.dpi=150

    if options.time_zone:
        time_zone = int(options.time_zone)
        if time_zone > 12: time_zone = 0
        if time_zone < -12: time_zone = 0
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
                    print _("Error reading plot_groups, resetting to '1'")
                    plot_groups = [0]
                plot_groups.sort()
            except:
                print _("Error groups, resetting to '1'")
                plot_groups = [1]
#    if len(plot_groups) == 1:
#        print "%d group has been selected: " % (len(plot_groups)), plot_groups
#    else:
#        print "%d groups have been selected: " % (len(plot_groups)), plot_groups    
    
    plot = VOAP2PPlot(data_file, 
                    data_type = int(options.data_type), 
                    plot_groups = plot_groups, 
                    plot_contours = options.plot_contours,
                    plot_label = options.plot_label,
                    color_map=options.color_map,
                    time_zone = time_zone,
                    plot_max_freq = plot_max_freq,
                    plot_bands = bands,
                    run_quietly = options.run_quietly,
                    save_file = options.save_file,
                    dpi = options.dpi)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main(sys.argv[-1])
    else:
        print 'voaP2PPlot error: No data file specified'
        print 'voaP2PPlot [options] filename'
        sys.exit(1)

      

