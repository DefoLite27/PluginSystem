from .EventHandler import BindableEvent
import builtins

class API:
    def __init__(self, pluginManager):
        self.pluginManager = pluginManager
        self.pluginFunctions = {}
        self.events = {}

        pluginManager.events["OnPluginRemove"].Connect(self._onPluginRemove)

    def getPlugin(self, name):
        """
        Get a plugin by its name (not visual name).
        """
        return self.pluginManager.getPlugin(name)

    def _addEvent(self, name):
        """
        Add an event to the API. This is a wrapper for the BindableEvent class.
        """
        if name not in self.events:
            self.events[name] = {
                "event": BindableEvent(builtins.sharedEventData, name),
            }

            def autoDestroy(event, *args, **kwargs):
                if self.events[name]["event"].connections == 0:
                    self.events[name].destroy()
                    del self.events[name]
            
            self.events[name]["event"].Connect(autoDestroy, True)

        return self.events[name]
    
    def connectEvent(self, name, function, once = False):
        """
        Connect a function to an event. This is a wrapper for the BindableEvent class.
        """
        self._addEvent(name)
        
        connection = self.events[name]["event"].Connect(function, once)

        return connection

    def _onPluginRemove(self, pluginName):
        for name, data in list(self.pluginFunctions.items()):
            if data["plugin"] == pluginName:
                del self.pluginFunctions[name]