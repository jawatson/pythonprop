#! /usr/bin/env python
#
# File: voaAreaPlot.py
#
# Copyright (c) 2008 J.Watson
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
# Work well:    cyl mill sinu
# Displays ok    ortho eqdc robin moll tmerc
# Displays ?:    lcc aea
# Crashes:    geos aeqd cass poly gnom stere laea
# Additional parameters required : splaea nplaea merc npstere  spstere npaeqd omerc spaeqd
#    print options.projection


#todo
# Label size need reducing on small plots
# Try and delete the frame on ortho plots
# All defaults should be defined in the same way, in the same place
# The matplotlib AxesGrid toolkit is a collection of helper classes to ease displaying multiple images in matplotlib. The AxesGrid toolkit is distributed with matplotlib source. DOH!
import re
import sys
import math
import datetime

import matplotlib
try:
    from mpl_toolkits.basemap import Basemap
except:
	pass

from gi.repository import Gtk
#matplotlib.use('GTK3Agg')

from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from numpy import ma #for warping


from optparse import OptionParser
import pylab as P

from voaAreaRect import *
from voaFile import *
from hamlocation import *
from voaPlotWindow import *
from sun import *
"""
try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GObject
except:
    pass
try:
    from gi.repository import Gtk
except:
    sys.exit(1)
"""

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



class VOAAreaPlot:

    IMG_TYPE_DICT  = { \
        1:{'plot_type':'MUF', 'title':_('Maximum Usable Frequency (MUF)'), 'min':2, 'max':30, 'y_labels':(2, 5, 10, 15, 20, 25, 30), 'formatter':'frequency_format', 'first_char':27, 'last_char':32}, \
        2:{'plot_type':'REL', 'title':_('Circuit Reliability (%)'), 'min':0, 'max':1, 'y_labels':(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 'formatter':'percent_format', 'first_char':98, 'last_char':104}, \
        3:{'plot_type':'SNR', 'title':_('SNR at Receiver (dB)'), 'min':20, 'max':70, 'y_labels':(20, 30, 40, 50, 60, 70), 'formatter':'SNR_format', 'first_char':86, 'last_char':92}, \
        4:{'plot_type':'SNRXX', 'title':_('SNRxx'), 'min':0, 'max':100, 'y_labels':(0, 20, 40, 60, 80, 100), 'formatter':'SNR_format', 'first_char':130, 'last_char':134}, \
        5:{'plot_type':'SDBW', 'title':_('Signal Power'), 'min':-160, 'max':-40, 'y_labels':(-160, -140, -120, -100, -80, -60, -40), 'formatter':'SDBW_format', 'first_char':74, 'last_char':80}, \
        6:{'plot_type':'SMETESNRXXR', 'title':_('S-Meter'), 'min':-151.18, 'max':-43.01, 'y_labels':(-151.18, -139.13, -127.09, -115.05, -103.01, -83.01, -63.01, -43.01), 'formatter':'SMETER_format', 'first_char':74, 'last_char':80} }

    COLOUR_MAPS = [ _('autumn'), _('bone'), _('cool'), _('copper'), _('gray'), \
                _('hot'), _('hsv'), _('jet'), _('pink'), _('spring'), \
                _('summer'), _('winter') ]

    default_font = {'family' : 'sans-serif'}
    show_subplot_frame = True
    
    def __init__(self, in_file,
                    vg_files = [1],
                    data_type = 1, 
                    projection = 'cyl',                
                    color_map = 'jet',
                    face_colour = "white",
                    time_zone = 0,
                    plot_contours = False,
                    plot_center = 't',
                    plot_meridians = True,
                    plot_parallels = True, 
                    plot_terminator = True,
                    resolution = 'c',
                    points_of_interest = [],
                    save_file = '',
                    run_quietly = False,
                    dpi = 150,
                    parent = None):

        self.run_quietly = run_quietly
        self.dpi=float(dpi)

        plot_parameters = VOAFile((in_file+'.voa'))
        plot_parameters.parse_file()
    
        if (plot_parameters.get_projection() != 'cyl'):
            print _("Error: Only lat/lon (type 1) input files are supported")
            sys.exit(1)

        grid = plot_parameters.get_gridsize()
        self.image_defs = VOAAreaPlot.IMG_TYPE_DICT[int(data_type)]

        # TODO This needs a little more work... what if the pcenter card is not specified
    
        if plot_center == 'p':
            plot_centre_location = plot_parameters.get_location(plot_parameters.P_CENTRE)
        else:        
            plot_centre_location = plot_parameters.get_location(plot_parameters.TX_SITE)
    
        self.points_of_interest = [plot_centre_location]        
        if len(points_of_interest) > 0:
            self.points_of_interest.extend(points_of_interest)

        imageBuf = P.zeros([grid, grid], float)

        area_rect = plot_parameters.get_area_rect()

        # The checks ought to be performed in the area_rect.
        # Do a few basic sanity checks #
        #if ( (area_rect.get_sw_lon() < -180) or (area_rect.get_ne_lon() > 180.0) or (area_rect.get_sw_lat() < -90) or (area_rect.get_ne_lat() > 90.0) ):
        #    print "Input file latitudes/longitudes are out of range"
        #    print "-180 < Latitude < 180.0, -90 < Longitude < 90"
        #    sys.exit(1)
        #if ( (area_rect.get_sw_lon() == area_rect.get_ne_lon()) or (area_rect.get_sw_lat() == area_rect.get_ne_lat()) ):
        #    print "Input file latitudes/longitudes are the same"
        #    print "-180 < Latitude < 180.0, -90 < Longitude < 90"
        #    sys.exit(1)

        points = P.zeros([grid,grid], float)
        lons = P.zeros(grid*grid, float) 
        lats = P.zeros(grid*grid, float)
    
        lons = P.arange(area_rect.get_sw_lon(), area_rect.get_ne_lon()+0.001,(area_rect.get_ne_lon()-area_rect.get_sw_lon())/float(grid-1))
        lats = P.arange(area_rect.get_sw_lat(), area_rect.get_ne_lat()+0.001,(area_rect.get_ne_lat()-area_rect.get_sw_lat())/float(grid-1))
    
        colString = 'P.cm.'+color_map
        colMap = eval(colString)
    
        self.subplots = []        
        self.number_of_subplots = len(vg_files)
        
        matplotlib.rcParams['axes.edgecolor'] = 'gray'
        matplotlib.rcParams['axes.facecolor'] = 'white'
        matplotlib.rcParams['figure.facecolor'] = face_colour
        #matplotlib.rcParams['figure.figsize'] = (6, 10)
        matplotlib.rcParams['figure.subplot.hspace'] = 0.45
        matplotlib.rcParams['figure.subplot.wspace'] = 0.35
        matplotlib.rcParams['figure.subplot.right'] = 0.85
        colorbar_fontsize = 12
                        
        if self.number_of_subplots <= 1:    
            self.num_rows = 1
            self.main_title_fontsize = 24
            matplotlib.rcParams['legend.fontsize'] = 12
            matplotlib.rcParams['axes.labelsize'] = 12
            matplotlib.rcParams['axes.titlesize'] = 10
            matplotlib.rcParams['xtick.labelsize'] = 10
            matplotlib.rcParams['ytick.labelsize'] = 10
            matplotlib.rcParams['figure.subplot.top'] = 0.8 # single figure plots have a larger title so require more space at the top.
        elif ((self.number_of_subplots >= 2) and (self.number_of_subplots <= 6 )):
            self.num_rows = 2
            self.main_title_fontsize = 18
            matplotlib.rcParams['legend.fontsize'] = 10
            matplotlib.rcParams['axes.labelsize'] = 10
            matplotlib.rcParams['axes.titlesize'] = 11
            matplotlib.rcParams['xtick.labelsize'] = 8
            matplotlib.rcParams['ytick.labelsize'] = 8
            #self.x_axes_ticks = P.arange(0,25,4)
        else:
            self.num_rows = 3
            self.main_title_fontsize = 16
            matplotlib.rcParams['legend.fontsize'] = 8
            matplotlib.rcParams['axes.labelsize'] = 8
            matplotlib.rcParams['axes.titlesize'] = 10
            matplotlib.rcParams['xtick.labelsize'] = 6
            matplotlib.rcParams['ytick.labelsize'] = 6
            #self.x_axes_ticks = P.arange(0,25,4)        
        
        self.num_cols = int(math.ceil(float(self.number_of_subplots)/float(self.num_rows)))  
        self.fig=Figure()      
        self.main_title_label = self.fig.suptitle(unicode(self.image_defs['title'],'utf-8'), fontsize=self.main_title_fontsize)
        
        if projection == 'ortho':
            self.show_subplot_frame = False
    
        for plot_ctr in range(self.number_of_subplots):
            #ax = self.fig.add_subplot(plot_ctr)
            ax = self.fig.add_subplot(self.num_rows, 
                    self.num_cols, 
                    plot_ctr+1,
                    frame_on = self.show_subplot_frame,
                    axisbg = 'white')            

            self.subplots.append(ax)
                        
            ax.label_outer()
            #print "opening: ",(in_file+'.vg'+str(vg_files[plot_ctr]))
            vgFile = open(in_file+'.vg'+str(vg_files[plot_ctr]))
            pattern = re.compile(r"[a-z]+")
    
            for line in vgFile:
                match = pattern.search( line )
                if not match:
                    value = float(line[int(self.image_defs['first_char']):int(self.image_defs['last_char'])]) 
                    # TODO Does this need to be normalised here if it's also being done in the plot?
                    value = max(self.image_defs['min'], value)
                    value = min(self.image_defs['max'], value)
                    #if value < self.image_defs[2] : value = self.image_defs[2] 
                    #if value > self.image_defs[3] : value = self.image_defs[3] 
                    points[int(line[3:6])-1][int(line[0:3])-1] = value
            vgFile.close()

            map = Basemap(\
                llcrnrlon=area_rect.get_sw_lon(), llcrnrlat=area_rect.get_sw_lat(),\
                urcrnrlon=area_rect.get_ne_lon(), urcrnrlat=area_rect.get_ne_lat(),\
                projection=projection,\
                lat_0=plot_centre_location.get_latitude(),\
                lon_0=plot_centre_location.get_longitude(),\
                resolution=resolution,
                ax=ax)
                
            map.drawcoastlines(color='black')
            map.drawcountries(color='grey')
            map.drawmapboundary(color='black', linewidth=1.0)
    
            warped = ma.zeros((grid, grid),float)
            warped, warped_lon, warped_lat = map.transform_scalar(points,lons,lats,grid,grid, returnxy=True, checkbounds=False, masked=True)
            warped = warped.filled(self.image_defs['min']-1.0)
            
            colMap.set_under(color ='k', alpha=0.0)
        
            im = map.imshow(warped,
                cmap=colMap,
                extent = (-180, 180, -90, 90),
                origin = 'lower',
                norm = P.Normalize(clip = False,
                vmin=self.image_defs['min'],
                vmax=self.image_defs['max']))


            #######################
            # Plot greyline
            #######################
            if plot_terminator:
                the_sun = Sun()
                the_month = plot_parameters.get_month(vg_files[plot_ctr]-1)
                the_day = plot_parameters.get_day(vg_files[plot_ctr]-1)
                the_hour = plot_parameters.get_utc(vg_files[plot_ctr]-1)
                if (the_day == 0):
                    the_day = 15
                the_year = datetime.date.today().year
                num_days_since_2k = the_sun.daysSince2000Jan0(the_year, the_month, the_day)
    
                res =  the_sun.sunRADec(num_days_since_2k)
                declination = res[1]
                if(declination==0.0):
                    declination=-0.001
    
                tau = the_sun.computeGHA(the_day, the_month, the_year, the_hour);
    
                if declination > 0:
                    terminator_end_lat = area_rect.get_sw_lat()
                else:
                    terminator_end_lat = area_rect.get_ne_lat()              
                  
                terminator_lat = [terminator_end_lat]
                terminator_lon = [area_rect.get_sw_lon()]
                
                for i in range(int(area_rect.get_sw_lon()),int(area_rect.get_ne_lon()),1)+[int(area_rect.get_ne_lon())]:
                    longitude=i+tau;
                    tan_lat = - the_sun.cosd(longitude) / the_sun.tand(declination)
                    latitude = the_sun.atand(tan_lat)
                    latitude = max(latitude, area_rect.get_sw_lat())
                    latitude = min(latitude, area_rect.get_ne_lat())
                    xpt, ypt = map(i, latitude)
                    terminator_lon.append(xpt)
                    terminator_lat.append(ypt)
    
                terminator_lon.append(area_rect.get_ne_lon())
                terminator_lat.append(terminator_end_lat)
                
                #This is a little simplistic and doesn't work for ortho plots....
                ax.plot(terminator_lon, terminator_lat, color='grey', alpha=0.75)
                ax.fill(terminator_lon, terminator_lat, facecolor='grey', alpha = 0.5)
    
                tau = -tau 
                if (tau > 180.0):
                    tau = tau-360.0
                if (tau < -180.0):
                    tau = tau+360.0
    
                #Plot the position of the sun (if it's in the coverage area)
                if area_rect.contains(declination, tau):
                    xpt,ypt = map(tau,declination) 
                    #sbplt_ax.plot([xpt],[ypt],'yh') 
                    ax.plot([xpt],[ypt],'yh') 

            ##########################   
            # Points of interest
            ##########################
            for location in self.points_of_interest: 
                if area_rect.contains(location.get_latitude(), location.get_longitude()):
                    xpt,ypt = map(location.get_longitude(),location.get_latitude()) 
                    ax.plot([xpt],[ypt],'ro') 
                    ax.text(xpt+100000,ypt+100000,location.get_name())
    
            if plot_meridians:
                if (area_rect.get_lon_delta() <= 90.0):
                    meridians = P.arange(-180, 190.0, 10.0)
                elif (area_rect.get_lon_delta() <= 180.0):
                    meridians = P.arange(-180.0, 210.0, 30.0)
                else:
                    meridians = P.arange(-180, 240.0, 60.0)
                if ((projection == 'ortho')    or (projection == 'vandg')):
                    map.drawmeridians(meridians)
                else:    
                    map.drawmeridians(meridians,labels=[1,1,0,1])
    
            if plot_parallels:
                if (area_rect.get_lat_delta() <= 90.0):
                    parallels = P.arange(-90.0, 120.0, 60.0)
                else:
                    parallels = P.arange(-90.0, 120.0, 30.0)
                if ((projection == 'ortho')    or (projection == 'vandg')):
                    map.drawparallels(parallels)
                else:    
                    map.drawparallels(parallels,labels=[1,1,0,1])
    
            if plot_contours:
                map.contour(warped_lon, warped_lat, warped, self.image_defs['y_labels'], linewidths=1.0, colors='k', alpha=0.5)

            #add a title
            
            title_str = plot_parameters.get_plot_description_string(vg_files[plot_ctr]-1, self.image_defs['plot_type'], time_zone)
            if self.number_of_subplots == 1:
                title_str = plot_parameters.get_plot_description_string(vg_files[plot_ctr]-1, self.image_defs['plot_type'], time_zone)
                title_str = title_str + "\n" + plot_parameters.get_detailed_plot_description_string(vg_files[plot_ctr]-1)
            else :
                title_str = plot_parameters.get_minimal_plot_description_string(vg_files[plot_ctr]-1, self.image_defs['plot_type'], time_zone)
            self.subplot_title_label = ax.set_title(title_str)

        # Add a colorbar on the right hand side, aligned with the 
        # top of the uppermost plot and the bottom of the lowest
        # plot.
        self.cb_ax = self.fig.add_axes(self.get_cb_axes())
        self.fig.colorbar(im, cax=self.cb_ax, 
                    orientation='vertical',
                    ticks=self.image_defs['y_labels'],
                    format = P.FuncFormatter(eval('self.'+self.image_defs['formatter'])))
        
        #print self.image_defs['y_labels']
        for t in self.cb_ax.get_yticklabels():
            t.set_fontsize(colorbar_fontsize)
        
        canvas = FigureCanvasGTK3Agg(self.fig)
        self.fig.canvas.mpl_connect('draw_event', self.on_draw)
        canvas.show()
        
        if save_file :
            self.save_plot(canvas, save_file)

        #todo this ought to a command line param
        if not self.run_quietly:
            dia = VOAPlotWindow('pythonProp - ' + self.image_defs['title'], canvas, parent=parent)
        return

    def on_draw(self, event):
        top = self.fig.subplotpars.top
        bottom = self.fig.subplotpars.bottom
        hspace = self.fig.subplotpars.hspace
        wspace = self.fig.subplotpars.wspace
        
        fig_height = self.fig.get_figheight()

        needs_adjusting = False

        # Area required at the top of the plot (Main title and subplot title)
        bbox = self.subplot_title_label.get_window_extent()
        subplot_title_bbox = bbox.inverse_transformed(self.fig.transFigure)
        
        bbox = self.main_title_label.get_window_extent()
        main_title_bbox = bbox.inverse_transformed(self.fig.transFigure)   
        
    
        _preferred_top_space = 1.25*(subplot_title_bbox.height + main_title_bbox.height)
        _actual_top_space = 1-top        

        if (_actual_top_space < _preferred_top_space) or ((_actual_top_space - _preferred_top_space)>0.11):
            top = 0.99 - _preferred_top_space
            needs_adjusting = True
         
        if needs_adjusting:  
            self.fig.subplots_adjust(top = top, bottom = bottom, hspace = hspace, wspace = wspace)
            self.cb_ax.set_position(self.get_cb_axes()) 
            self.fig.canvas.draw()
        return False
   

    def save_plot(self, canvas, filename=None):
        canvas.print_figure(filename, dpi=self.dpi, facecolor=self.fig.get_facecolor(), edgecolor='none')


    def get_cb_axes(self):    
        bbox = self.subplots[0].get_window_extent()
        axis_upper_y = bbox.inverse_transformed(self.fig.transFigure).ymax
        bbox = self.subplots[-1].get_window_extent()
        axis_lower_y = bbox.inverse_transformed(self.fig.transFigure).ymin
        return [0.87, axis_lower_y, 0.02, axis_upper_y-axis_lower_y]
        
        
    def percent_format(self, x, pos):
        return '%(percent)3d%%' % {'percent':x*100} 

    def SNR_format(self, x, pos):
        return '%3ddB' % x
    
    def SDBW_format(self, x, pos):
        return '%3ddBW' % x
            		
    """
    The values below are derived from material
    presented at http://www.voacap.com/s-meter.html
    """
    def SMETER_format(self, x, pos):
        print x 
        S_DICT = {-151.18:'S1', -145.15:'S2', -139.13:'S3', -133.11:'S4', -127.09:'S5', \
                    -121.07:'S6', -115.05:'S7', -109.03:'S8', -103.01:'S9', -93.01:'S9+10dB', \
                    -83.01:'S9+20dB', -73.01:'S9+30dB', -63.01:'S9+40dB', -53.01:'S9+50dB', -43.01:'S9+60dB'}
        if S_DICT.has_key(x):
        	return '%s' % S_DICT[x]
            #return _('%(value)ddBW (%(s_value)s)') %{'value':x, 's_value':S_DICT[x]}
        else : return '%3d' % x     


    def frequency_format(self, x, pos):
        return '%2dMHz' % x


    def default_format(self, x, pos):
        return '%d' % x


def main(in_file):
    #todo read the version from a central string...
    parser = OptionParser(usage="%voaAreaPlot [options] file", version="%voaAreaPlot 0.9.1")
    parser.disable_interspersed_args()
    #tested ok
    parser.add_option("-c", "--contours", 
        dest = "plot_contours", 
        action = "store_true", 
        default = False,
        help = _("Enables contour plotting.") )
    #tested ok    
    parser.add_option("-d", "--datatype", 
        dest="data_type", 
        default=1,
        help=_("DATATYPE - an integer number representing the data to plot. Valid values are 1 (MUF), 2 (REL) and 3 3 (SNR) 4 (SNRxx), 5 (SDBW) and 6 (SDBW - formatted as S-Meter values).  Default value is 1 (MUF).") )

    parser.add_option("-e", "--centre", 
        dest="plot_centre", 
        default='t',
        choices = [ 'p', 't'],
        help = _("Defines the plot centre on circular (e.g. ortho) plots.  Ignored on cylindrical plots.  Valid values are 't' (Tx. Site), 'p' (PCenter).  Default is 't'"))
    #tested ok    
    parser.add_option("-i", "--meridian", 
        dest="plot_meridians",
        action="store_true", 
        default=False, 
        help=_("Plot meridians."))
    parser.add_option("-k", "--background", 
        dest="face_colour", 
        default='white',
        help=_("Specify the colour of the background. Any legal HTML color specification is supported e.g '-k red', '-k #eeefff' (default = white)"))
    #tested ok        
    parser.add_option("-l", "--parallels", 
        dest="plot_parallels",
        action="store_true", 
        default=False,
        help=_("Plot meridians."))
    #tested ok
    parser.add_option("-m", "--cmap", 
        dest = "color_map", 
        default = 'jet',
        choices = [ 'autumn', 'bone', 'cool', 'copper', 'gray', \
                'hot', 'hsv', 'jet', 'pink', 'spring','summer', 'winter' ],
        help=_("COLOURMAP - may be one of 'autumn', 'bone', 'cool', 'copper', 'gray', 'hot', 'hsv', 'jet', 'pink', 'spring', 'summer', 'winter'.  Default = 'jet'"))
    #tested ok
    parser.add_option("-n", "--interest", 
        dest = "poi_file", 
        default = '',
        help = "poi_file is a text file with points to plot on the map.")
    parser.add_option("-o", "--outfile", 
        dest="save_file",
        help="Save to FILE.", metavar="FILE")
    #tested ok
    parser.add_option("-p", "--projection", 
        dest="projection",  
        default = 'cyl',
        choices = ['cyl', 'mill', 'sinu', 'ortho', 'eqdc', 'robin', 'moll', 'tmerc', 'vandg'],
        help=_("PROJECTION - may be one of 'cyl' = Cylindrical Equidistant (default), 'mill' = Miller Cylindrical, 'sinu' = Sinusoidal, 'ortho' = Orthographic, 'eqdc' = Equidistant Conic, 'robin' = Robinson, 'moll' = Mollweide, 'tmerc' = Transverse Mercator."))
    parser.add_option("-q", "--quiet",
        dest="run_quietly",
        action="store_true",  
        default=False,
        help=_("Process quietly (don't display plot on the screen)"))
    #tested ok
    parser.add_option("-r", "--resolution", 
        dest="resolution", 
        default = 'c',
        choices = ['c', 'l', 'i', 'h', 'f'],
        help=_("RESOLUTION - may be one of 'c' (crude), 'l' (low), 'i' (intermediate), 'h' (high), 'f' (full)"))
    # tested ok

    parser.add_option("-s", "--size",
        dest="dpi",
        default=150,
        help=_("Dots per inch (dpi) of saved file."))
        
    parser.add_option("-t", "--terminator", 
        dest="plot_terminator", 
        action="store_true", 
        default = False,
        help=_("Plot day/night regions on map"))

    parser.add_option("-v", "--vg_files", 
        dest = "vg_files", 
        default = '1',
        help=_("VG_FILES number of plots to process, e.g '-v 1,3,5,6' or use '-v a' to print all plots.") )
    #tested ok
    parser.add_option("-z", "--timezone", 
        dest="timezone", 
        default=0,
        help=_("Time zone (integer, default = 0)"))

    if in_file.endswith('.voa'):
        in_file = in_file.split(".voa")[0] #TODO: this needs to be more robust...

    (options, args) = parser.parse_args()

    points_of_interest = []
    vg_files = []
    if options.poi_file:
        try:    
            f = open(options.poi_file, 'r')
            for line in f:
                if len(line) > 3:
                    tokens = line.strip().split(',', 2)
                    #lat = float(tokens[1].strip())
                    #lon = float(tokens[0].strip())
                    #name = tokens[2].strip()
                    points_of_interest.append(HamLocation(lat = float(tokens[1].strip()), 
                                                lon = float(tokens[0].strip()), 
                                                name = tokens[2].strip()))
        except:
            print _("Error reading points of interest file: %s") % options.poi_file
            print sys.exc_info()[0]
            points_of_interest = []
    else:
        points_of_interest = []
  
    if options.data_type:
        if not VOAAreaPlot.IMG_TYPE_DICT.has_key(int(options.data_type)):
            print _("Unrecognised plot type: Defaulting to MUF")
            options.dataType = 1

    if options.vg_files:
        options.vg_files.strip()
        if options.vg_files == 'a':
            #'all' option see if the file exists and add it to the list
            for file_num in range (1, 13):
                if os.path.exists(in_file+'.vg'+str(file_num)):
                    print _("found: "),(in_file+'.vg'+str(file_num))
                    vg_files.append(file_num)
        else:
            try:
                if options.vg_files.find(','):
                    vg_files = options.vg_files.split(',')
                else:
                    vg_files = [options.vg_files]

                for i in range(0, len(vg_files)):
                    try:
                        vg_files[i] = int(vg_files[i])
                    except:
                        vg_files.pop(i)
                if len(vg_files) == 0:
                    print _("Error reading vg files (1), resetting to '1'")
                    vg_files = [1]
            except:
                print _("Error reading vg files, resetting to '1'")
                vg_files = [1]
        print _("The following %d files have been selected: ") % (len(vg_files)), vg_files 

    if options.timezone:
        time_zone = int(options.timezone)
        if time_zone > 12: time_zone = 0
        if time_zone < -12: time_zone = 0
    else :
        time_zone = 0
    
    #todo ortho doesn't work with the day/night terminator
        
    VOAAreaPlot(in_file, 
                    vg_files = vg_files,
                    time_zone = time_zone, 
                    data_type = options.data_type,
                    projection = options.projection,
                    color_map = options.color_map,
                    face_colour = options.face_colour,
                    plot_contours = options.plot_contours,
                    plot_meridians = options.plot_meridians,
                    plot_parallels = options.plot_parallels,
                    plot_terminator = options.plot_terminator,
                    resolution = options.resolution,
                    points_of_interest = points_of_interest,
                    save_file = options.save_file,
                    run_quietly = options.run_quietly,
                    dpi = options.dpi)
    

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main(sys.argv[-1])
    else:
        print 'voaAreaPlot error: No data file specified'
        print 'voaAreaPlot [options] filename'
        sys.exit(1)

