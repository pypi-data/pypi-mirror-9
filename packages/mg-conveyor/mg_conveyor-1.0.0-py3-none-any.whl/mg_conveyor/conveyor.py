import yapsy.PluginManager as yPM
from mg_conveyor.plugin_interfaces import ISequencialPlugin
from mg_conveyor.plugin_interfaces import IUtilityPlugin
from mg_conveyor.exceptions import ConveyorError

import logging

'''
Created on 18/01/2015

@author: RonElla
'''

STATUS_SUCCESS=0
STATUS_FAILED=-1
STATUS_ABORT=10
STATUS_RETRY=20
STATUS_CONFIRM_RETRY=30
STATUS_CONFIRM_ABORT=40
STATUS_CONTINUE=50
STATUS_SKIPPED=60
STATUS_STARTED=70

CONTEXT_KEY_STATUS = "STATUS"
CONTEXT_KEY_PLUGIN_OBJECT = "PLUGIN_OBJECT"

class Conveyor(object):
    '''
    classdocs
    '''
    
    __context = {}

    def getSortedPlugins(self):
        return self.__sortedPlugins
    
    def getPluginFolders(self):
        return self.__pluginFolders
    
    def getPluginManager(self):
        return self.__manager
    
    def __init__(self):
        self.__LOG = logging.getLogger("Conveyor")
        
        self.__plugins = []
        self.__sortedPlugins = []
        self.__pluginFolders = []
        self.__utilityPlugins = []
        self.__manager = None
        self.__context = {}
            
    def loadPlugins(self, pluginFolders, *args, **kwargs):
        
        self.__LOG.debug("def loadPlugins(self, pluginFolders)")
        
        self.__pluginFolders = pluginFolders
        
        self.__manager = yPM.PluginManager()
        self.__manager.setPluginPlaces(self.__pluginFolders)
        self.__manager.setCategoriesFilter({
            "SequencialPlugin" : ISequencialPlugin,
            "UtilityPlugin" : IUtilityPlugin
        })
        self.__manager.collectPlugins()
                
        self.__plugins = self.__manager.getAllPlugins()
        
        if self.__plugins:
            for plugin in self.__plugins:
                plugin_object = plugin.plugin_object
                plugin_name = plugin.name
                
                self.__LOG.debug("Plugin " + str(plugin) + " [" + plugin_name + "]")
                self.__LOG.debug("Plugin Object " + str(plugin_object))
                self.__context[plugin_name] = {}
                
                if isinstance(plugin_object, ISequencialPlugin) or isinstance(plugin_object, IUtilityPlugin):
                    self.__context[plugin_name][CONTEXT_KEY_PLUGIN_OBJECT] = plugin_object
                    
                    if isinstance(plugin_object, ISequencialPlugin):
                        self.__sortedPlugins.append(plugin)
                    elif isinstance(plugin_object, IUtilityPlugin):
                        plugin_object.context = self.__context
                        plugin_object.identity = plugin_name
                        self.__utilityPlugins.append(plugin)
                
                else:
                    self.__LOG.debug("Ignoring " + plugin_name + " plugin.")
            
            self.__sortedPlugins=sorted(self.__sortedPlugins
                , key=lambda sortedPlugin: sortedPlugin.plugin_object.sequence())
                                                
        else:
            self.__LOG.debug("No plugins found.")
            
    def __logError(self, msg, *args, **kwargs):
        logError = lambda err: self.__LOG.error(err)
        
        if 'conv_logError' in kwargs:
            logError = kwargs['conv_logError']
            
        logError(msg)
        
    def __logDebug(self, msg, *args, **kwargs):
        logDebug = lambda err: self.__LOG.debug(err)
        
        if 'conv_logDebug' in kwargs:
            logDebug = kwargs['conv_logDebug']
            
        logDebug(msg)
            
    def start(self, *args, **kwargs):
        self.__LOG.debug("def start(self, *args, **kwargs)")
        
        for plugin in self.__sortedPlugins: 
            plugin_identity = plugin.name
            try:
                status = kwargs.get('conv_status', plugin.plugin_object.process(plugin_identity, self.__context, *args, **kwargs))
            except ConveyorError as ex:
                self.__LOG.error(ex)
                status = STATUS_FAILED

            self.__context[plugin_identity][CONTEXT_KEY_STATUS] = status
            
            if 'conv_context' in kwargs:
                kwargs['conv_context'](plugin_identity, self.__context)
                
            self.__LOG.debug("Context: " + str(self.__context))
            
            if status == STATUS_FAILED:
                self.__logError("Error occurred.", *args, **kwargs)
                break
            elif status == STATUS_ABORT:
                self.__logDebug("Aborting.", *args, **kwargs)
                break
            elif status == STATUS_CONTINUE:
                self.__logDebug("Continuing to next.", *args, **kwargs)
                continue
            elif status == STATUS_SKIPPED:
                self.__logDebug("Skipped to next plugin.", *args, **kwargs)
                continue
            elif status == STATUS_RETRY:
                responseStatus = {'Y': STATUS_CONFIRM_RETRY, 'N': STATUS_CONFIRM_ABORT}

                if 'conv_retry' in kwargs:
                    response = kwargs['conv_retry']
                else:
                    response = input("Retry? Yn")

                retryResponse = lambda ans: self.__LOG.debug(ans)
                
                if 'conv_retryResponse' in kwargs: 
                    retryResponse = kwargs['conv_retryResponse']
                
                try:
                    
                    try:
                        response = responseStatus[str(response).upper()]
                        
                        if response == STATUS_CONFIRM_RETRY:
                            retryResponse("Will retry")
                            continue
                        elif response == STATUS_CONFIRM_ABORT:
                            retryResponse("Will abort")
                            break

                    except KeyError as ex:
                        raise ConveyorError("Not a valid response for Retry? Aborting.")
                    
                except ConveyorError as ex:
                    self.__logError(ex.message, *args, **kwargs)
                    break