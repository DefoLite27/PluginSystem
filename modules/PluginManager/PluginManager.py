from pathlib import Path
import builtins
import os

from ..jsonFunctions import getJsonData
from ..API import API
from ..logger import info, warn, success, error
from ..EventHandler import BindableEvent
import threading

# 

class PluginManager:
    def __init__(self):
        self.managerData = getJsonData(Path(__file__).parent / 'managerData.json')
        self.pluginsFolder = Path(__file__).parent.parent.parent / 'plugins'

        self.plugins = {}
        self.events = {
            "OnPluginRemove": BindableEvent(builtins.sharedEventData, "OnPluginRemove"),
        }

        self.api = API(self)

    def loadPlugins(self):
        info("Loading plugins.")

        for pluginFolder in self.pluginsFolder.iterdir():
            if pluginFolder.is_dir() and (pluginFolder / 'plugin.py').exists():
                self._loadPlugin(pluginFolder)

    def _loadPlugin(self, pluginFolder):
        pluginData = getJsonData(pluginFolder / 'config.json')
        folderName = pluginFolder.name

        # Checks
        if not pluginData['enabled']:
            warn(f"Plugin \"{pluginData['visualName']}\" was not loaded because it's disabled.")
            return

        if pluginData['loaderVersion'] not in self.managerData['supportedVersions']:
            warn(f"Plugin \"{pluginData['visualName']}\" was not loaded because it's not compatible with this version of the API. "
                 f"(API: {self.managerData['version']}, Plugin: {pluginData['loaderVersion']})")
            return

        if folderName in self.plugins:
            warn(f"Plugin \"{pluginData['visualName']}\" was not loaded because it's already loaded.")
            return
        
        dependecies = pluginData['dependencies']
        def addDependencies(pluginFolder):
            PluginData = getJsonData(pluginFolder / "config.json")
            for p in self.pluginsFolder.iterdir():
                dependencyData =  getJsonData(p / "config.json")
                if dependencyData['name'] in PluginData['dependencies'] and not dependencyData['name'] in dependecies:
                    dependecies.append(dependencyData['name'])
                    addDependencies(p)
        addDependencies(pluginFolder)
                
        for dependency in dependecies:
            if not any(getJsonData(p / "config.json")['name'] == dependency for p in self.pluginsFolder.iterdir()):
                warn(f"Plugin \"{pluginData['visualName']}\" was not loaded because it depends on plugin \"{dependency}\" which is not found.")
                return
            else:
                dependencyPluginFold = None
                for p in self.pluginsFolder.iterdir():
                    if getJsonData(p / "config.json")['name'] == dependency:
                        dependencyPluginFold = p

                dependencyPluginData = getJsonData(dependencyPluginFold / "config.json")
                if dependencyPluginData["version"] < pluginData["dependencies"][dependency]:
                    warn(f"Plugin \"{pluginData['visualName']}\" was not loaded because it depends on plugin \"{dependency}\" which is outdated. "
                         f"(API: {self.managerData['version']}, Plugin: {dependencyPluginData['version']})")
                    return

        # Load the plugin
        try:
            module = __import__(f'plugins.{folderName}.plugin', fromlist=['Plugin'])
            pluginClass = getattr(module, 'Plugin')
            
            plugin = pluginClass(self.api)
            plugin.currentPath = pluginFolder
            plugin.init()
            plugin.onLoad()
            plugin.loaded = True

            self.plugins[folderName] = plugin
            success(f"Plugin \"{pluginData['visualName']}\" was successfully loaded.")
        except Exception as e:
            error(f"Failed to load plugin \"{pluginData['visualName']}\": {e}")

    def startPlugins(self):
        info("Starting plugins.")

        self._checkAllPluginDependencies()

        for plugin in self.plugins.values():
            self._startPlugin(plugin)

        self.cleanPlugins()

    def _checkAllPluginDependencies(self):
        def checkDependencies():
            for plugin in self.plugins.values():
                for dependency in plugin.configData['dependencies']:
                    if not any(p.configData['name'] == dependency for p in self.plugins.values()):
                        warn(f"Plugin \"{plugin.configData['visualName']}\" was not started because it depends on plugin \"{dependency}\" which is not loaded.")
                        self._removePlugin(plugin)
                        return False
                    else:
                        dependencyPlugin = next(p for p in self.plugins.values() if p.configData['name'] == dependency)
                        if dependencyPlugin.configData["version"] < plugin.configData["dependencies"][dependency]:
                            warn(f"Plugin \"{plugin.configData['visualName']}\" was not started because it depends on plugin \"{dependency}\" which is outdated. "
                                f"(API: {self.managerData['version']}, Plugin: {dependencyPlugin.configData['version']})")
                            self._removePlugin(plugin)
                            return False
            return True
        returned = checkDependencies()
        while not returned:
            returned = checkDependencies()

    def _startPlugin(self, plugin):
        if plugin.started:
            warn(f"Plugin \"{plugin.configData['visualName']}\" was not started because it's already started.")
            return
        
        if not plugin.loaded:
            return
        
        thread = threading.Thread(target=plugin.start)
        thread.start()
        plugin.started = True

        success(f"Plugin \"{plugin.configData['visualName']}\" was successfully started.")

    def _removePlugin(self, plugin):
        plugin.onRemove()
        plugin.cleanUp()

        folder = next((name for name, p in self.plugins.items() if p == plugin), None)
        if folder:
            del self.plugins[folder]
            self.events["OnPluginRemove"].Fire(plugin.configData['name'])
            success(f"Plugin \"{plugin.configData['visualName']}\" was successfully removed.")

    def cleanPlugins(self):
        info("Cleaning plugins.")

        self._checkAllPluginDependencies()

        toRemove = [plugin for plugin in self.plugins.values() if not plugin.loaded or not plugin.started]

        for plugin in toRemove:
            self._removePlugin(plugin)

    def getPlugin(self, name):
        """
        Get a plugin by its name (not visual name).
        """
        return next((plugin for plugin in self.plugins.values() if plugin.configData['name'] == name), None)