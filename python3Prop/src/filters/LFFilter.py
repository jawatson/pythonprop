

class LPFilter:
    '''
    A filter designed by Gwyn Williams (G4FKH) and used when
    preparing RSGB propagation predictions.
    '''
 
    def __init__(dictionary):
    '''
    dictionary is a list of parameter names and corresponding
    index.  The init function should check the dictionary to 
    verify that all required keys (data) are in place, rasieing
    a KeyError if a required key is not found.
    ''' 
        self.keys = dictionary
        required_keys = ('FREQ', 'LAT', 'LON')
        for key in required_keys:
          if key not in dictionary:
              raise KeyError


    def apply_filter(self, fields):
    '''
    Apply the filter to the fields and return the modified row.
    
    '''
        pass
'''
// Filter 1
IF (FREQUENCY < 12MHz) AND (E-PATH FIELD STRENGTH < 15.92) AND (Tx-Rx DISTANCE < 3600KM)
	SET BCR->0, E-PATH->0

// Filter 2
IF (OPMUF10 < FREQUENCY)
	SET BCR->0, E-PATH->0

// Filter 3
IF (BCR < 1)
	SET BCR->0, E-PATH->0
'''
