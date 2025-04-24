# Do not remove
import os
from modules.PluginManager.Plugin import Plugin 
###

class Plugin(Plugin):
    def onLoad(self):
        # Do not remove
        self.currentPath = os.path.dirname(os.path.abspath(__file__)) 
        self.init(self.currentPath) 
        self.loaded = True
        ###

        #print("Plugin loaded")

    def start(self):
        # Do not remove
        self.started = True
        ###
        
        #print("Plugin started")

    def onRemove(self):
        
        #print("Plugin removed")
        
        self.cleanUp()