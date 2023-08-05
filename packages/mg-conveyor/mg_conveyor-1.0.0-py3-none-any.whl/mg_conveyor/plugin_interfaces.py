import yapsy.IPlugin as yPlugin

'''
Created on 21/01/2015

@author: ronaldow
'''

class ISequencialPlugin(yPlugin.IPlugin):
    
    def __init__(self):
        super().__init__()
    
    def sequence(self):
        raise NotImplementedError()
    
    def process(self, identity, context, *args, **kwargs):
        raise NotImplementedError()
    
class IUtilityPlugin(yPlugin.IPlugin):
    
    def __init__(self):
        super().__init__()
        self.__context = {}
        self.__identity = {}
        
    @property
    def context(self):
        return self.__context
    
    @context.setter
    def context(self, context):
        self.__context=context
        
    @property
    def identity(self):
        return self.__identity
    
    @identity.setter
    def identity(self, identity):
        self.__identity=identity
        
    @property
    def localContext(self):
        return self.context[self.identity]
        
    def use(self, *args, **kwargs):
        raise NotImplementedError()
