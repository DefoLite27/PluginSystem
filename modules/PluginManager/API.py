import builtins

from ..EventHandler import BindableEvent
from ..logger import warn, error, info

class API:
    def __init__(self, pluginManager):
        self.pluginManager = pluginManager
        self.events = {}
        self.dataSpace = {} # This is a space for plugins to store data that can be accessed by other plugins.

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

    def fireEvent(self, name, *args, **kwargs):
        """
        Fire an event. This is a wrapper for the BindableEvent class.
        """
        if name in self.events:
            self.events[name]["event"].Fire(*args)

    def _onPluginRemove(self, pluginName):
        return

    def changePluginOptions(self, plugin, optionName, kwargs):
        if not optionName in plugin.configData["options"]:
            error(f"Plugin \"{plugin.configData['visualName']}\" does not have option \"{optionName}\".")
            return
        
        optionType = plugin.configData["options"][optionName]["type"]
        valueBefore = plugin.configData["options"][optionName]["value"]

        if optionType == "bool":
            plugin.configData["options"][optionName]["value"] = kwargs.get("value", False)
        elif optionType == "selector":
            newValue = kwargs.get("value", None)
            if newValue == None:
                error("No value provided")
            if newValue in plugin.configData["options"][optionName]["selectOptions"]:
                plugin.configData["options"][optionName]["value"] = newValue
            else:
                error(f"Trying to change an option in selector which does not exist. Plugin: \"{plugin.configData["visualName"]}\", Option: \"{optionName}\", Value: \"{newValue}\"")

        if valueBefore != plugin.configData["options"][optionName]["value"]:
            plugin.optionsChanged(optionName, kwargs)

    