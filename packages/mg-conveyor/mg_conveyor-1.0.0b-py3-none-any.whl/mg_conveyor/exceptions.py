'''
Created on 30/01/2015

@author: ronaldow
'''

class ConveyorError(Exception):

    def __init__(self, message):
        self.__message = message
        
    
    def __str__(self):
        return repr(self.__message)
    
    @property
    def message(self):
        return self.__message