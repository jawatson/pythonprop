
import datetime
import sys

from optparse import OptionParser

import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap

from rec533Out import REC533Out

class PropAreaPlot:

    def __init__(self, data_file,
            list_files = False,
            data_opt = 'SNR',
            plot_files = 1,
            plot_terminator = False,
            dpi = 150):

        self.plot_terminator = plot_terminator
        self.dpi = dpi

        self.r533 = REC533Out(data_file)

        if list_files:
            self.dump_datasets()
            quit()

        if plot_files == 'a':
            print("doing all of the plots")
            quit
        else:
            for dataset_id in plot_files:
                # todo don't expose the datasets here
                if dataset_id < len(self.r533.datasets):
                    dataset = self.r533.get_plot_data(dataset_id, data_opt)
                    self.do_plot(dataset)
                else:
                    print ("Invalid index", dataset_id)

    def do_plot(self, dataset):
        #for dataset in r533:
        points, plot_type, lons, lats, num_pts_lon, num_pts_lat, params = dataset
        plot_dt, plot_title, freq, idx = params
        #plt.figure(figsize=(12,6))
        m = Basemap(projection='cyl', resolution='l')
        m.drawcoastlines(color='black', linewidth=0.75)
        m.drawcountries(color='grey')
        m.drawmapboundary(color='black', linewidth=1.0)
        m.drawmeridians(np.arange(0,360,30))
        m.drawparallels(np.arange(-90,90,30))

        X,Y = np.meshgrid(lons, lats)

        #todo remove hard-coded values for vmin and vmax
        #im = m.pcolormesh(X, Y, points, shading='gouraud', cmap=plt.cm.jet, latlon=True, vmin=-20, vmax=40)
        #im = m.pcolormesh(X, Y, points, shading='gouraud', cmap=plt.cm.jet, latlon=True, vmin=-20, vmax=40)
        im = m.imshow(points, interpolation='bilinear', vmin=0, vmax=100)

        if self.plot_terminator:
            m.nightshade(plot_dt)

        cb = m.colorbar(im,"bottom", size="5%", pad="2%")
        plt.title(plot_title)

        plot_fn = "area_{:s}_{:s}_{:s}.png".format(plot_type, plot_dt.strftime("%H%M_%b_%Y"), "d".join(str(freq).split('.')))
        print ("Saving file ", plot_fn)
        plt.savefig(plot_fn, dpi=float(self.dpi), bbox_inches='tight')

        #plt.show()


    def dump_datasets(self):
        ds_list = self.r533.get_datasets()
        print("ID\tUTC Title Frequency")
        for ctr, ds in enumerate(ds_list):
            plot_dt, freq, title = ds
            print('{: 4d}  {:s}\t{:6.3f}\t{:}'.format(ctr, plot_dt.strftime("%H:%M %b %Y"), float(freq), title))


def main(data_file):
    parser = OptionParser(usage="propAreaPlot [options] file", version="propAreaPlot 0.9.1")
    parser.disable_interspersed_args()

    parser.add_option("-d", "--datatype",
        dest="data_opt",
        type='choice',
        choices=['SNR', 'REL'],
        default='SNR',
        help=("DATATYPE - a string representation of the data to plot. Valid values are 'SNR' and 'REL'. Default value is 'SNR'.") )

    parser.add_option("-g", "--grey-line",
        dest="plot_terminator",
        action="store_true",
        default = False,
        help=("Plot day/night regions on map"))

    parser.add_option("-l", "--list",
        dest = "list",
        action="store_true",
        default = False,
        help=("List files and quit.") )

    parser.add_option("-p", "--plots",
        dest = "plot_files",
        default = '1',
        help=("Plots to print, e.g '-v 1,3,5,6' or use '-v a' to print all plots.") )

    parser.add_option("-r", "--resolution",
        dest="dpi",
        default=150,
        help=("Dots per inch (dpi)."))
    (options, args) = parser.parse_args()

    plot_files = []
    if options.plot_files and not options.list:
        options.plot_files.strip()
        if options.plot_files == 'a':
            plot_files = 'a'
        # todo if not defined
        else:
            try:
                plot_files = hyphen_range(options.plot_files)
            except:
                print ("Error reading plot datasets; resetting to '1'")
                plot_files = [1]

        print ("The following {:d} files have been selected {:s}: ".format(len(plot_files), str(plot_files)))

    PropAreaPlot(data_file,
                data_opt = options.data_opt,
                list_files = options.list,
                plot_files = plot_files,
                plot_terminator = options.plot_terminator,
                dpi = options.dpi)


def hyphen_range(s):
    """ Takes a range in form of "a-b" and generate a list of numbers between a and b inclusive.
    Also accepts comma separated ranges like "a-b,c-d,f" will build a list which will include
    Numbers from a to b, a to d and f"""
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
