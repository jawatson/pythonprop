import sys
from random import randint

from propAreaPlot import PropAreaPlot

class CallingClass:
    '''
    A simple script to demonstrate / test calling the ploting routines
    from an external class.
    '''

    def __init__(self, f):
        pp = PropAreaPlot(f)
        ds_list = pp.get_datasets()
        for i in range(3):
            ds_id = randint(0,len(ds_list))
            print("Plotting dataset ID {:d}.".format(ds_id))
            print(ds_list[ds_id])
            pp.plot_datasets((ds_id,), 'SNR')

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        cc = CallingClass(sys.argv[-1])
    else:
        print ('Error: No data file specified')
        sys.exit(1)
