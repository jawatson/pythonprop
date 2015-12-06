
from hamlocation import HamLocation

class LFFilter:
    '''
    A filter designed by Gwyn Williams (G4FKH) and used when
    preparing RSGB propagation predictions.
    '''

    def __init__(self, dictionary):
        '''
        dictionary is a list of parameter names and corresponding
        index.  The init function should check the dictionary to
        verify that all required keys (data) are in place, rasieing
        a KeyError if a required key is not found.

        The month, hour and frequency are in all dictionaries, in
        indexes 0, 1 & 2 respectively.
        '''
        self.keys = dictionary
        required_keys = ('REL', 'OPMUF10', 'E')
        for key in required_keys:
          if key not in dictionary:
              raise KeyError ("Warning: Unable to apply LFFilter - {:s} field not found in data file.".format(key))

        #todo don't hardcode this
        self.tx_location = HamLocation(lat=54.5, lon=2.0)

    def apply_filter(self, fields):
        '''
        The RSGB filtering comprises three steps;

        Filter 1
        IF (FREQUENCY < 12MHz) AND (E-PATH FIELD STRENGTH < 15.92) AND (Tx-Rx DISTANCE < 3600KM)
        	SET BCR->0, E-PATH->0

        Filter 2
        IF (OPMUF10 < FREQUENCY)
        	SET BCR->0, E-PATH->0

        Filter 3
        IF (BCR < 1)
        	SET BCR->0, E-PATH->0
        '''
        freq_idx = int(self.keys['FREQ'])
        e_idx = int(self.keys['E'])

        rx_location = HamLocation(lat=float(fields[self.keys['RX_LAT']]), lon=float(fields[self.keys['RX_LON']]))
        bearing, distance = self.tx_location.path_to(rx_location)

        if (float(fields[freq_idx]) < 12.0) and (float(fields[e_idx]) < 15.92) and (distance < 3600):
            print ("Calculated Distance: {:3.2f}km".format(distance))
            print (fields)
            fields[self.keys['REL']] = 0.00
            fields[self.keys['E']] = 0.00
            print (fields)

        return fields
