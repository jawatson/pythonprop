#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
import io
import os
import re
import sys
import math
import datetime

import matplotlib
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap
#from mpl_toolkits.basemap import Basemap
import cartopy.crs as ccrs


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

from matplotlib.ticker import FuncFormatter
import numpy as np
import numpy.ma as ma

from optparse import OptionParser

import zipfile

from .voaAreaRect import VOAAreaRect
from .voaFile import VOAFile
from .hamlocation import HamLocation
from .voaPlotWindow import *

from .vgzArchive import get_base_filename


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
                    filled_contours = False,
                    plot_contours = False,
                    plot_center = 't',
                    plot_meridians = True,
                    plot_parallels = True,
                    plot_nightshade = True,
                    resolution = 'c',
                    points_of_interest = [],
                    save_file = '',
                    run_quietly = False,
                    dpi = 150,
                    parent = None,
                    datadir=None):

        self.run_quietly = run_quietly
        self.dpi=float(dpi)

        self.datadir = datadir

        try:
            plot_parameters = VOAFile((in_file))
            plot_parameters.parse_file()
        except zipfile.BadZipFile as e:
            if parent is None:
                print("Invalid .vgz file")
                sys.exit(1)

        if (plot_parameters.get_projection() != 'cyl'):
            print(_("Error: Only lat/lon (type 1) input files are supported"))
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

        imageBuf = np.zeros([grid, grid], float)

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

        #colString = 'matplotlib.cm.'+color_map
        #colMap = eval(colString)
        portland = ListedColormap(["#0C3383", "#0b599b","#0a7fb4","#57a18f","#bec255","#f2c438","#f2a638","#ef8235","#e4502a","#d91e1e"])
        plt.register_cmap(name='portland', cmap=portland)
        colMap = color_map


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

        #self.fig=Figure()
        #https://github.com/SciTools/cartopy/issues/899
        proj=ccrs.PlateCarree()
        self.fig, axes = plt.subplots(1, 1, squeeze=False, subplot_kw=dict(projection=proj))

        self.main_title_label = self.fig.suptitle(str(self.image_defs['title']), fontsize=self.main_title_fontsize)

        #plt.cla()

        for plot_idx, vg_file in enumerate(vg_files):
            print('Doing plot ', plot_idx)
            col_idx = int(plot_idx/self.num_cols)
            row_idx = plot_idx%self.num_cols
            points = np.zeros([grid,grid], float)

            lons = np.arange(area_rect.get_sw_lon(), area_rect.get_ne_lon()+0.001,(area_rect.get_ne_lon()-area_rect.get_sw_lon())/float(grid-1))
            lons[-1] = min(180.0, lons[-1])
            lats = np.arange(area_rect.get_sw_lat(), area_rect.get_ne_lat()+0.001,(area_rect.get_ne_lat()-area_rect.get_sw_lat())/float(grid-1))
            lats[-1] = min(90.0, lats[-1])

            axes[col_idx][row_idx].label_outer()
            if in_file.endswith('.vgz'):
                base_filename = get_base_filename(in_file)
                zf = zipfile.ZipFile(in_file)
                vgFile = io.TextIOWrapper(zf.open("{:s}.vg{:d}".format(base_filename, vg_file)), 'utf-8')
            else:
                vgFile = open("{:s}.vg{:d}".format(os.path.splitext(in_file)[0], vg_file))
            pattern = re.compile(r"[a-z]+")

            for line in vgFile:
                match = pattern.search( line )
                if not match:
                    value = float(line[int(self.image_defs['first_char']):int(self.image_defs['last_char'])])
                    # TODO Does this need to be normalised here if it's also being done in the plot?
                    value = max(self.image_defs['min'], value)
                    value = min(self.image_defs['max'], value)
                    points[int(line[3:6])-1][int(line[0:3])-1] = value
            vgFile.close()
            if 'zf' in locals():
                zf.close()

            def resize_colorbar(event):
                plt.draw()
                posn = axes[col_idx][row_idx].get_position()
                cbar_ax.set_position([posn.x0 + posn.width + 0.01, posn.y0,
                                      0.02, posn.height])

            self.fig.canvas.mpl_connect('resize_event', resize_colorbar)


            axes[col_idx][row_idx].coastlines()

            #points = np.clip(points, self.image_defs['min'], self.image_defs['max'])
            #colMap.set_under(color ='k', alpha=0.0)
            lons, lats  = np.meshgrid(lons, lats)
            points = np.clip(points, self.image_defs['min'], self.image_defs['max'])

            axes[col_idx][row_idx].set_extent([area_rect.get_sw_lon(),
                                                area_rect.get_ne_lon(),
                                                area_rect.get_sw_lat(),
                                                area_rect.get_ne_lat()], ccrs.PlateCarree())

            if (filled_contours):
                im = axes[col_idx][row_idx].contourf(lons, lats, points, self.image_defs['y_labels'],
                    cmap = colMap,
                    transform=ccrs.PlateCarree())
                plot_contours = True
            else:
                im = axes[col_idx][row_idx].pcolormesh(lons, lats, points,
                    vmin = self.image_defs['min'],
                    vmax = self.image_defs['max'],
                    cmap = colMap,
                    transform=ccrs.PlateCarree())

            if plot_contours:
                ct = axes[col_idx][row_idx].contour(lons, lats, points, self.image_defs['y_labels'][1:],
                    linestyles='solid',
                    linewidths=0.5,
                    colors='k',
                    vmin=self.image_defs['min'],
                    vmax=self.image_defs['max'],
                    transform=ccrs.PlateCarree())
            #######################
            # Plot greyline
            #######################
            #if plot_nightshade:
            #    m.nightshade(plot_parameters.get_daynight_datetime(vg_files[plot_ctr]-1))


            ##########################
            # Points of interest
            ##########################
            """
            for location in self.points_of_interest:
                if area_rect.contains(location.get_latitude(), location.get_longitude()):
                    xpt,ypt = m(location.get_longitude(),location.get_latitude())
                    ax.plot([xpt],[ypt],'ro')
                    ax.text(xpt+100000,ypt+100000,location.get_name())

            if plot_meridians:
                if (area_rect.get_lon_delta() <= 90.0):
                    meridians = np.arange(-180, 190.0, 10.0)
                elif (area_rect.get_lon_delta() <= 180.0):
                    meridians = np.arange(-180.0, 210.0, 30.0)
                else:
                    meridians = np.arange(-180, 240.0, 60.0)
                if ((projection == 'ortho')    or (projection == 'vandg')):
                    m.drawmeridians(meridians)
                else:
                    m.drawmeridians(meridians,labels=[1,1,0,1])

            if plot_parallels:
                if (area_rect.get_lat_delta() <= 90.0):
                    parallels = np.arange(-90.0, 120.0, 60.0)
                else:
                    parallels = np.arange(-90.0, 120.0, 30.0)
                if ((projection == 'ortho')    or (projection == 'vandg')):
                    m.drawparallels(parallels)
                else:
                    m.drawparallels(parallels,labels=[1,1,0,1])
            """

            #add a title
            title_str = plot_parameters.get_plot_description_string(vg_files[plot_idx]-1, self.image_defs['plot_type'], time_zone)
            if self.number_of_subplots == 1:
                title_str = plot_parameters.get_plot_description_string(vg_files[plot_idx]-1, self.image_defs['plot_type'], time_zone)
                title_str = title_str + "\n" + plot_parameters.get_detailed_plot_description_string(vg_files[plot_idx]-1)
            else :
                title_str = plot_parameters.get_minimal_plot_description_string(vg_files[plot_idx]-1, self.image_defs['plot_type'], time_zone)
            self.subplot_title_label = axes[col_idx][row_idx].set_title(title_str)

        # Add a colorbar on the right hand side, aligned with the
        # top of the uppermost plot and the bottom of the lowest
        # plot.
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.
        """
        if self.number_of_subplots > 1:
            self.cb_ax = self.fig.add_axes(self.get_cb_axes())
        else:
            divider = make_axes_locatable(ax)
            self.cb_ax = divider.append_axes("right", size="5%", pad=0.05)
        self.fig.colorbar(im, cax=self.cb_ax,
                    orientation='vertical',
                    ticks=self.image_defs['y_labels'],
                    format = FuncFormatter(eval('self.'+self.image_defs['formatter'])))
        """

        #print self.image_defs['y_labels']
        """
        for t in self.cb_ax.get_yticklabels():
            t.set_fontsize(colorbar_fontsize)
        """
        # Add the colorbar axes anywhere in the figure. Its position will be
        # re-calculated at each figure resize.
        cbar_ax = self.fig.add_axes([0, 0, 0.1, 0.1])
        cbar_ax.tick_params(labelsize=10)

        self.fig.subplots_adjust(hspace=0, wspace=0, top=0.925, left=0.05)

        plt.colorbar(im,
            cax=cbar_ax,
            ticks = self.image_defs['y_labels'],
            format = FuncFormatter(eval('self.'+self.image_defs['formatter'])))

        #self.fig.tight_layout()
        canvas = FigureCanvas(self.fig)
        #self.fig.canvas.mpl_connect('draw_event', self.on_draw)
        resize_colorbar(None)

        canvas.show()

        if save_file :
            self.save_plot(canvas, save_file)

        #todo this ought to a command line param
        if not self.run_quietly:
            dia = VOAPlotWindow('pythonProp - ' + self.image_defs['title'], canvas, parent=parent, datadir=self.datadir)
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
        S_DICT = {-151.18:'S1', -145.15:'S2', -139.13:'S3', -133.11:'S4', -127.09:'S5', \
                    -121.07:'S6', -115.05:'S7', -109.03:'S8', -103.01:'S9', -93.01:'S9+10dB', \
                    -83.01:'S9+20dB', -73.01:'S9+30dB', -63.01:'S9+40dB', -53.01:'S9+50dB', -43.01:'S9+60dB'}
        if x in S_DICT:
        	return '%s' % S_DICT[x]
            #return _('%(value)ddBW (%(s_value)s)') %{'value':x, 's_value':S_DICT[x]}
        else : return '%3d' % x


    def frequency_format(self, x, pos):
        return '%2dMHz' % x


    def default_format(self, x, pos):
        return '%d' % x


def main(in_file, datadir=None):
    parser = OptionParser(usage="%voaAreaPlot [options] file")
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

    parser.add_option("--filled-contour",
        dest = "plot_filled_contours",
        action = "store_true",
        default = False,
        help = _("Produces a filled contour plot.") )

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

    parser.add_option("-m", "--cmap",
        dest = "color_map",
        default = 'jet',
        choices = [ 'autumn', 'bone', 'cool', 'copper', 'gray', \
                'hot', 'hsv', 'jet', 'pink', 'spring','summer', 'winter', 'portland' ],
        help=_("COLOURMAP - may be one of 'autumn', 'bone', 'cool', 'copper', 'gray', 'hot', 'hsv', 'jet', 'pink', 'spring', 'summer', 'winter' or 'portland'.  Default = 'jet'"))

    parser.add_option("-n", "--interest",
        dest = "poi_file",
        default = '',
        help = "poi_file is a text file with points to plot on the map.")

    parser.add_option("-o", "--outfile",
        dest="save_file",
        help="Save to FILE.",
        metavar="FILE")

    parser.add_option("-p", "--projection",
        dest="projection",
        default = 'cyl',
        choices = ['cyl', 'mill', 'gall', 'robin', 'vandg', 'sinu', 'mbtfpq',
                    'eck4', 'kav7', 'moll', 'hammer', 'cass', 'poly', 'gnom',
                    'laea', 'aeqd', 'cea', 'merc'])

    parser.add_option("-q", "--quiet",
        dest="run_quietly",
        action="store_true",
        default=False,
        help=_("Process quietly (don't display plot on the screen)"))

    parser.add_option("-r", "--resolution",
        dest="resolution",
        default = 'c',
        choices = ['c', 'l', 'i', 'h', 'f'],
        help=_("RESOLUTION - may be one of 'c' (crude), 'l' (low), 'i' (intermediate), 'h' (high), 'f' (full)"))

    parser.add_option("-s", "--size",
        dest="dpi",
        default=150,
        help=_("Dots per inch (dpi) of saved file."))

    parser.add_option("-t", "--terminator",
        dest="plot_nightshade",
        action="store_true",
        default = False,
        help=_("Plot day/night regions on the map"))

    parser.add_option("-v", "--vg_files",
        dest = "vg_files",
        default = '1',
        help=_("VG_FILES number of plots to process, e.g '-v 1,3,5,6' or use '-v a' to print all plots.") )
    #tested ok
    parser.add_option("-z", "--timezone",
        dest="timezone",
        default=0,
        help=_("Time zone (integer, default = 0)"))

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
            print(_("Error reading points of interest file: %s") % options.poi_file)
            print(sys.exc_info()[0])
            points_of_interest = []
    else:
        points_of_interest = []

    if options.data_type:
        if int(options.data_type) not in VOAAreaPlot.IMG_TYPE_DICT:
            print(_("Unrecognised plot type: Defaulting to MUF"))
            options.dataType = 1

    if options.vg_files:
        options.vg_files.strip()
        if options.vg_files == 'a':
            #'all' option see if the file exists and add it to the list
            for file_num in range (1, 13):
                if os.path.exists(in_file+'.vg'+str(file_num)):
                    print(_("found: "),(in_file+'.vg'+str(file_num)))
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
                    print(_("Error reading vg files (1), resetting to '1'"))
                    vg_files = [1]
            except:
                print(_("Error reading vg files, resetting to '1'"))
                vg_files = [1]
        #print(_("The following %d files have been selected: ") % (len(vg_files)), vg_files)

    if options.timezone:
        time_zone = int(options.timezone)
        if time_zone > 12: time_zone = 0
        if time_zone < -12: time_zone = 0
    else :
        time_zone = 0

    VOAAreaPlot(in_file,
                    vg_files = vg_files,
                    time_zone = time_zone,
                    data_type = options.data_type,
                    projection = options.projection,
                    color_map = options.color_map,
                    face_colour = options.face_colour,
                    filled_contours = options.plot_filled_contours,
                    plot_contours = options.plot_contours,
                    plot_meridians = options.plot_meridians,
                    plot_parallels = options.plot_parallels,
                    plot_nightshade = options.plot_nightshade,
                    resolution = options.resolution,
                    points_of_interest = points_of_interest,
                    save_file = options.save_file,
                    run_quietly = options.run_quietly,
                    dpi = options.dpi,
                    datadir=datadir)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main(sys.argv[-1])
    else:
        print('voaAreaPlot error: No data file specified')
        print('voaAreaPlot [options] filename')
        sys.exit(1)
