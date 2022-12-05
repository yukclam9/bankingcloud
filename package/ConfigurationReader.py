import fileinput
import os
import logging

class ConfigurationReader:

    
    def __init__(self,configurationFilename,comment='#',delimiter='='):
        self._allConfigurations=dict()
        self.configurationFile = configurationFilename
        self.comment= comment
        self.delimiter=delimiter
        self.lg = logging.getLogger(__name__)
        self.parseConfiguration()
        
    def skipEmptyAndCommented(self,f):
        for line in f:
            l = line.strip()
            if l and not l.startswith(self.comment):
                yield l


    def readLinesToDict(self,f):
        for line in self.skipEmptyAndCommented(f):
            configuration = dict()
            #print(line)
            keyPair= dict([line.split(self.delimiter)])
            #print(keyPair)
            self._allConfigurations.update(keyPair)
            
    def parseConfiguration(self):
        with open(os.path.join( self.configurationFile ),'r') as inFile:
            self.readLinesToDict(inFile)
                  

    def returnKey(self,key):
        return self._allConfigurations[key]

    
    @property
    def allConfigurations(self):
        for key in self._allConfigurations:
            self.lg.debug(f'{key} has value of {self._allConfigurations[key]}')
        return self._allConfigurations

    @allConfigurations.setter
    def allConfigurations(self,value):
        # can only append, never replace
        if isinstance(value,dict):
            self.lg.info(f'Append value to configuration : {value}')
            self._allConfigurations.update(value)
        for key in self._allConfigurations:
            self.lg.debug(f'{key} has value of {self._allConfigurations[key]}')
