#! /usr/bin/env python
#
# File: VOAMultiPlot
# Version: 121208
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

# A small class to handle multiple plots on a single figure
# VOAMultiPlot acts as a layout manager for the plotting.
# Eventualy this class will be able to determine the correct font
# size etc. for the plots

#import matplotlib   
from matplotlib.figure import Figure   
from matplotlib.font_manager import FontProperties
import math


class VOAMultiPlot(Figure):
    ax = [] # a list to hold all the subplot axes

    def __init__(self, number_of_subplots):
        Figure.__init__(self)
        self.number_of_subplots = number_of_subplots
        
        #todo
        # there has to be an existing class that can hold four points together
        # Determine how multiple plots will be laid out, 2x1, 3x4 etc.
        if self.number_of_subplots <= 1:    
            self.num_rows = 1
            self.title_fontsize = 12
            self.legend_fontsize = 12
            self.axes_label_fontsize = 12
            self.axes_tick_fontsize = 10
            self.main_border_left = 0.05
            self.main_border_right = 0.05
            self.main_border_lower = 0.05
            self.main_border_upper = 0.05
            self.subplot_border_left = 0.0
            self.subplot_border_right = 0.0            
            self.subplot_border_lower = 0.05
            self.subplot_border_upper = 0.2
        elif ((self.number_of_subplots >= 2) and (self.number_of_subplots <= 6 )):
            self.num_rows = 2
            self.title_fontsize = 10
            self.legend_fontsize = 10
            self.axes_label_fontsize = 10
            self.axes_tick_fontsize = 8
            self.main_border_left = 0.05
            self.main_border_right = 0.05
            self.main_border_lower = 0.0
            self.main_border_upper = 0.05
            self.subplot_border_left = 0.0
            self.subplot_border_right = 0.0            
            self.subplot_border_lower = 0.05
            self.subplot_border_upper = 0.05
        else:
            self.num_rows = 3
            self.title_fontsize = 8
            self.legend_fontsize = 6
            self.axes_label_fontsize = 8
            self.axes_tick_fontsize = 6
            self.main_border_left = 0.05
            self.main_border_right = 0.05
            self.main_border_lower = 0.1
            self.main_border_upper = 0.0
            self.subplot_border_left = 0.0
            self.subplot_border_right = 0.0            
            self.subplot_border_lower = 0.0
            self.subplot_border_upper = 0.1
        
        self.num_cols = int(math.ceil(float(self.number_of_subplots)/float(self.num_rows)))    

        self.main_axes_width = 1.0 - (self.main_border_left + self.main_border_right)
        self.main_axes_height = 1.0 - (self.main_border_lower + self.main_border_upper)

        # Set up grid geometry
        self.col_width = (self.main_axes_width/self.num_cols)
        self.row_height = (self.main_axes_height/self.num_rows)

        self.subplot_width = self.col_width - (self.subplot_border_left + self.subplot_border_right) 
        self.subplot_height = self.row_height - (self.subplot_border_lower + self.subplot_border_upper)        


    def add_subplot(self, plot_number):
        ax_row_num = math.floor(float(plot_number) / float(self.num_cols))
        ax_col_num = plot_number - (ax_row_num * self.num_cols)
        
        subplot_x = self.main_border_left + (ax_col_num * self.col_width) + self.subplot_border_left
        subplot_y = self.main_border_lower + ((self.num_rows-1)-ax_row_num)*self.row_height + self.subplot_border_lower
        
        sbplt_ax = self.add_axes([subplot_x, subplot_y, self.subplot_width, self.subplot_height])
        self.ax.append(sbplt_ax)
        
        return sbplt_ax

    def set_main_title(self, aTitle):
        t = self.text(0.5, 0.93, aTitle, \
                horizontalalignment='center', \
                fontproperties=FontProperties(size=16))


    def get_title_fontsize(self):
        return self.title_fontsize

        
    def get_axes_label_fontsize(self):
        return self.axes_label_fontsize

        
    def get_legend_fontsize(self):
        return self.legend_fontsize
        
        
    def get_axes_tick_fontsize(self):
        return self.axes_tick_fontsize


    def get_figure(self):
        return mainFigure


    def add_colorbar(self, img_sample, cb_format):
        # make the colorbar vertical for 1-2 plots, horizontal for everything else
        # rect = l,b,w,h (left, bottom, width, height)
        if (self.num_cols == 1):
            cb_ax = self.add_axes([0.8, 0.2, 0.04, 0.5])
            self.colorbar(img_sample, cax=cb_ax, orientation='vertical', format = cb_format)
        else:
            cb_ax = self.add_axes([0.1, 0.04, 0.8, 0.04])
            self.colorbar(img_sample, cax=cb_ax, orientation='horizontal', format = cb_format)
    