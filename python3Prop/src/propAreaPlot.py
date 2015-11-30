
import datetime

import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap

from rec533Out import REC533Out

class PropAreaPlot:

    def __init__(self):
        r533 = REC533Out("area.out")
        points,lons,lats,num_pts_lon,num_pts_lat = r533.get_plot_data('01', '3.52')

        plt.figure(figsize=(12,6))
        m = Basemap(projection='cyl', resolution='l')
        m.drawcoastlines(color='black', linewidth=0.75)
        m.drawcountries(color='grey')
        m.drawmapboundary(color='black', linewidth=1.0)
        m.drawmeridians(np.arange(0,360,30))
        m.drawparallels(np.arange(-90,90,30))

        X,Y = np.meshgrid(lons, lats)

        #todo remove hard-coded values for vmin and vmax
        im = m.pcolormesh(X, Y, points, shading='gouraud', cmap=plt.cm.jet, latlon=True, vmin=-20, vmax=40)
        #im = m.imshow(points, interpolation='bilinear', vmin=-20, vmax=40)

        plot_dt = datetime.datetime(2015, 3, 15, hour=1)
        m.nightshade(plot_dt)

        cb = m.colorbar(im,"bottom", size="5%", pad="2%")
        #plt.title('Test ITU Image')

        plt.savefig('foo.png', dpi=400, bbox_inches='tight')

        plt.show()





if __name__ == "__main__":
    r533 = PropAreaPlot()
