
import datetime
import sys

import argparse

import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap

from rec533Out import REC533Out

class PropAreaPlot:

    IMG_TYPE_DICT  = { \
        'MUF':{'title':('MUF'), 'vmin':2, 'vmax':30, 'y_labels':(2, 5, 10, 15, 20, 25, 30), 'formatter':'frequency_format'}, \
        'REL':{'title':('Reliability (%)'), 'vmin':0, 'vmax':1, 'y_labels':(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), 'formatter':'percent_format'}, \
        'SNR':{'title':('SNR'), 'vmin':-10, 'vmax':70, 'y_labels':(20, 30, 40, 50, 60, 70), 'formatter':'SNR_format' }}


    def __init__(self, data_file):
        self.r533 = REC533Out(data_file)


    def plot_datasets(self, ds_list, data_opt, dpi = 150, plot_terminator=False):
        for dataset_id in ds_list:
            # todo don't expose the datasets here
            # do a check here to make sure the data_opt is supported
            try:
                plot_params = self.IMG_TYPE_DICT[data_opt]
            except KeyError:
                print("Error: Undefined plot type, {:s}".format(data_opt))
                return
            if dataset_id < len(self.r533.datasets):
                try:
                    self.do_plot(self.r533.get_plot_data(dataset_id, data_opt),
                        plot_params,
                        dpi=dpi,
                        plot_terminator = plot_terminator)
                except LookupError:
                    print("Error retrieving data for ID {:d}/{:s}.".format(dataset_id, data_opt))

            else:
                print ("Invalid index:", dataset_id)

    def do_plot(self, dataset, plot_params, dpi=150, plot_terminator=False):
        points, plot_type, lons, lats, num_pts_lon, num_pts_lat, params = dataset
        plot_dt, plot_title, freq, idx = params
        plt.cla() #Clear any existing plot data e.g. nightshade
        m = Basemap(projection='cyl', resolution='l')
        m.drawcoastlines(color='black', linewidth=0.75)
        m.drawcountries(color='grey')
        m.drawmapboundary(color='black', linewidth=1.0)
        m.drawmeridians(np.arange(0,360,30))
        m.drawparallels(np.arange(-90,90,30))

        X,Y = np.meshgrid(lons, lats)

        im = m.pcolormesh(X, Y, points, shading='gouraud', cmap=plt.cm.jet, latlon=True, vmin=plot_params['vmin'], vmax=plot_params['vmax'])

        #im = m.imshow(points, interpolation='bilinear', vmin=self.plot_params['vmin'], vmax=self.plot_params['vmax'])

        if plot_terminator:
            m.nightshade(plot_dt)

        cb = m.colorbar(im,"right", size="5%", pad="2%")
        plt.title("{:s} - {:s}".format(plot_title, plot_params['title']))

        plot_fn = "area_{:s}_{:s}_{:s}.png".format(plot_type, plot_dt.strftime("%H%M_%b_%Y"), "d".join(str(freq).split('.')))
        print ("Saving file ", plot_fn)
        plt.savefig(plot_fn, dpi=float(dpi), bbox_inches='tight')


    def get_datasets(self):
        ''' Returns a list of datasets found in the out file.'''
        return self.r533.get_datasets()

    def dump_datasets(self):
        ''' Dumps a list of datasets to the screen.'''
        ds_list = self.get_datasets()
        print("ID\tUTC Title Frequency")
        for ctr, ds in enumerate(ds_list):
            plot_dt, freq, title = ds
            print('{: 4d}  {:s}\t{:6.3f}\t{:}'.format(ctr, plot_dt.strftime("%H:%M %b %Y"), float(freq), title))


def main(data_file):
    parser = argparse.ArgumentParser(description="Plot HF Area Predictions.")
    subparsers = parser.add_subparsers()

    query_mode_parser = subparsers.add_parser('query', help="Query mode commands")
    plot_mode_parser = subparsers.add_parser('plot', help="Plot mode commands")

    plot_mode_parser.add_argument("-d", "--datatype",
        dest = "data_opt",
        choices = ['SNR', 'REL'],
        default = 'SNR',
        help = "DATATYPE - a string representation of the data to plot. Valid values are 'SNR' and 'REL'. Default value is 'SNR'." )

    plot_mode_parser.add_argument("-g", "--grey-line",
        dest = "plot_terminator",
        action = "store_true",
        default = False,
        help = "Plot day/night regions on map")

    query_mode_parser.add_argument("-l", "--list",
        dest = "list",
        action = "store_true",
        default = False,
        help = "List files and quit." )

    plot_mode_parser.add_argument("-p", "--plots",
        dest = "plot_files",
        default = '1',
        help = "Plots to print, e.g '-v 1,3,5,6' or use '-v a' to print all plots." )

    plot_mode_parser.add_argument("-r", "--resolution",
        dest = "dpi",
        type = int,
        default = 150,
        help = ("Dots per inch (dpi)."))

    parser.add_argument(dest = "data_file",
        help = "Name of the file containing the prediction data.")

    args = parser.parse_args()

    plot_files = []
    if hasattr(args, 'plot_files'):
        args.plot_files.strip()
        if args.plot_files == 'a':
            plot_files = 'a'
        # todo if not defined
        else:
            try:
                plot_files = hyphen_range(args.plot_files)
            except:
                print ("Error reading plot datasets; resetting to '1'")
                plot_files = [1]

        print ("The following {:d} files have been selected {:s}: ".format(len(plot_files), str(plot_files)))

    pp = PropAreaPlot(args.data_file)
    if hasattr(args, 'list'):
        pp.dump_datasets()
    else:
        pp.plot_datasets(plot_files,
            args.data_opt,
            plot_terminator=args.plot_terminator,
            dpi=args.dpi)

def hyphen_range(s):
    """ Takes a range in form of "a-b" and generate a list of numbers between a and b inclusive.
    Also accepts comma separated ranges like "a-b,c-d,f" will build a list which will include
    Numbers from a to b, a to d and f

    The following function was taken from;
    http://code.activestate.com/recipes/577279-generate-list-of-numbers-from-hyphenated-and-comma/
    """
    s="".join(s.split())#removes white space
    r=set()
    for x in s.split(','):
        t=x.split('-')
        if len(t) not in [1,2]: raise SyntaxError("Error parsing",s)
        r.add(int(t[0])) if len(t)==1 else r.update(set(range(int(t[0]),int(t[1])+1)))
    l=list(r)
    l.sort()
    return l


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main(sys.argv[-1])
    else:
        print ('propAreaPlot error: No data file specified')
        print ('propAreaPlot [options] filename')
        sys.exit(1)
