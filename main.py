from modules.PluginManager.PluginManager import PluginManager
from modules.jsonFunctions import getJsonData
from modules.EventHandler import createSharedEvents
import builtins

if __name__ == "__main__":
    settings = getJsonData('settings.json')
    builtins.settings = settings
    builtins.sharedEventData = createSharedEvents()

    pluginMan = PluginManager()
    pluginMan.loadPlugins()
    pluginMan.startPlugins()


# Upload to GitHub