# -*- coding: utf-8 -*-
# A simple class to bind an antenna filepath
# with it's description.

class VOAAntennaFile:
    description = ''
    filePath = ''
    
    def __init__(self, aPath, aDescription):
        self.description = aDescription
        self.filePath = aPath
        
    def get_filepath(self):
        return self.filePath
        
    def get_description(self):
        return self.description