#!/usr/bin/env python
"""
Show how to make date plots in matplotlib using date tick locators and
formatters.  See major_minor_demo1.py for more information on
controlling major and minor ticks

All matplotlib date plotting is done by converting date instances into
days since the 0001-01-01 UTC.  The conversion, tick locating and
formatting is done behind the scenes so this is most transparent to
you.  The dates module provides several converter functions date2num
and num2date

"""
from datetime import datetime
from datetime import date
import matplotlib
matplotlib.use('GTK3Agg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import matplotlib.dates as mdates
import matplotlib.mlab as mlab

from ssnFetch import *

class VOASSNThumb:

    def __init__(self, data_source):
        years    = mdates.YearLocator(2)   # every year
        months   = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%y')
        
        dt_list, ssn_list = data_source.get_plotting_data()
        
        self.figure = Figure(figsize=(12,8), dpi=72)   
        self.figure.patch.set_facecolor('white')
        self.figure.subplots_adjust(bottom=0.2)
        self.axis = self.figure.add_subplot(111) 
        self.axis.plot_date(dt_list, ssn_list, '-', lw=2)
        self.axis.axvline(date.today(), color='r')
        
        # format the ticks
        self.axis.xaxis.set_major_locator(years)
        self.axis.xaxis.set_major_formatter(yearsFmt)
        
        self.axis.grid(True)
        
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        # The following line currently breaks voacapgui if the thumbnail is 
        # inserted into a panel
        # self.figure.autofmt_xdate(rotation=90)
        
        self.canvas = FigureCanvas(self.figure) # a Gtk.DrawingArea   

        
    def get_thumb(self):
        return self.canvas
        
#short test routine
def main():
    s = SSNFetch(save_location="table_international-sunspot-numbers_monthly-predicted.txt")
    t = VOASSNThumb(s)
    graph = t.get_thumb()
    graph.show()
    first, last = s.get_data_range()
    dialog = Gtk.Dialog(title='ssn data')
    dialog.vbox.pack_start(graph, True, True, 0)
    dialog.set_default_size(350,250)
    dialog.run()


if __name__ == "__main__":
    main()
