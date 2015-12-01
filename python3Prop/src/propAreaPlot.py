
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
            plot_files = 1,
            plot_terminator = False,
            dpi = 150):

        self.r533 = REC533Out(data_file)

        if list_files:
            self.dump_datasets()
            quit()

        ctr = 1
        dataset = self.r533.get_plot_data(r533.datasets[1])
        #for dataset in r533:
        points, lons, lats, num_pts_lon, num_pts_lat, params = dataset
        plot_dt, freq, idx = params
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

        im = m.imshow(points, interpolation='bilinear', vmin=-20, vmax=40)

        if plot_terminator:
            m.nightshade(plot_dt)

        cb = m.colorbar(im,"bottom", size="5%", pad="2%")
        #plt.title('Test ITU Image')

        plot_fn = "area_{:d}_{:s}.png".format(plot_dt.month, "d".join(str(freq).split('.')))
        print ("Saving file ", plot_fn)
        plt.savefig(plot_fn, dpi=float(dpi), bbox_inches='tight')
        ctr += 1

        #plt.show()


    def dump_datasets(self):
        ds_list = self.r533.get_datasets()
        for ctr, ds in enumerate(ds_list):
            plot_dt, freq, idx = ds
            print('{:03d}  {:s}\t{:s}'.format(ctr, plot_dt.strftime("%b %Y"), freq))


def main(data_file):
    parser = OptionParser(usage="propAreaPlot [options] file", version="propAreaPlot 0.9.1")
    parser.disable_interspersed_args()

    parser.add_option("-d", "--dpi",
        dest="dpi",
        default=150,
        help=("Dots per inch (dpi)."))
    parser.add_option("-l", "--list",
        dest = "list",
        action="store_true",
        default = False,
        help=("List files and quit.") )
    parser.add_option("-p", "--plots",
        dest = "plot_files",
        default = '1',
        help=("Plots to print, e.g '-v 1,3,5,6' or use '-v a' to print all plots.") )
    parser.add_option("-t", "--terminator",
        dest="plot_terminator",
        action="store_true",
        default = False,
        help=("Plot day/night regions on map"))

    (options, args) = parser.parse_args()

    PropAreaPlot(data_file,
                list_files = options.list,
                plot_files = options.plot_files,
                plot_terminator = options.plot_terminator,
                dpi = options.dpi)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        main(sys.argv[-1])
    else:
        print ('propAreaPlot error: No data file specified')
        print ('propAreaPlot [options] filename')
        sys.exit(1)
