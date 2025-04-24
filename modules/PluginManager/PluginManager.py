from colorama import Fore, Style
from pathlib import Path
from ..jsonFunctions import getJsonData
from ..API import API

class PluginManager:
    def __init__(self):
        self.managerData = getJsonData(Path(__file__).parent / 'managerData.json')
        self.pluginsFolder = Path(__file__).parent.parent.parent / 'plugins'
        self.api = API(self)

        self.plugins = {}
        self.debug = True

    def loadPlugins(self):
        if self.debug:
            print(Fore.BLUE + "Loading all plugins." + Style.RESET_ALL)

        for pluginFolder in self.pluginsFolder.iterdir():
            if pluginFolder.is_dir() and (pluginFolder / 'plugin.py').exists(): # Skips any non plugin folders
                self._loadPlugin(pluginFolder)

    def _loadPlugin(self, pluginFolder):
        if pluginFolder.is_dir() and (pluginFolder / 'plugin.py').exists():
            pluginData = getJsonData(pluginFolder / 'config.json')
            folderName = pluginFolder.name
            pluginPath = pluginFolder / 'plugin.py'

            # Checks
            if pluginData['enabled'] == False:
                if self.debug:
                    print(Fore.YELLOW + "Plugin \"" + pluginData["visualName"] + "\" was not loaded because it's disabled." + Style.RESET_ALL)
                return
            
            if not pluginData['loaderVersion'] in self.managerData['supportedVersions']:
                if self.debug:
                    print(Fore.YELLOW + "Plugin \"" + pluginData["visualName"] + f"\" was not loaded because it's not compatible with this version of the API. (API: {self.managerData['version']}, Plugin: {pluginData['loaderVersion']})" + Style.RESET_ALL)
                return
            
            if folderName in self.plugins:
                if self.debug:
                    print(Fore.YELLOW + "Plugin \"" + pluginData["visualName"] + "\" was not loaded because it's already loaded." + Style.RESET_ALL)
                return
            ###

            if self.debug:
                print(Fore.GREEN + "Plugin \"" + pluginData["visualName"] + "\" was successfully loaded." + Style.RESET_ALL)

            module = __import__(f'plugins.{folderName}.plugin', fromlist=['Plugin'])
            pluginClass = getattr(module, 'Plugin')
            
            plugin = pluginClass(self.api)

            plugin.onLoad()

            self.plugins[folderName] = plugin

    def startPlugins(self):
        if self.debug:
            print(Fore.BLUE + "Starting plugins." + Style.RESET_ALL)
        
        for plugin in self.plugins.values():
            self._startPlugin(plugin)
        
        self.cleanPlugins()
    
    def _startPlugin(self, plugin):
        if plugin.started:
            if self.debug:
                print(Fore.YELLOW + "Plugin \"" + plugin.configData["visualName"] + "\" was not started because it's already started." + Style.RESET_ALL)
            return
        
        for dependency in plugin.configData['dependencies']:
            found = False
            for pluginToTest in self.plugins.values():
                if pluginToTest.configData['name'] == dependency:
                    found = True
                    break
            if not found:
                if self.debug:
                    print(Fore.YELLOW + "Plugin \"" + plugin.configData["visualName"] + "\" was not started because it depends on plugin \"" + dependency + "\" which is not loaded." + Style.RESET_ALL)
                return


        
        plugin.start()
        if self.debug:
            print(Fore.BLUE + "Plugin \"" + plugin.configData["visualName"] + "\" was successfully started." + Style.RESET_ALL)

    def _removePlugin(self, plugin):
        
        plugin.onRemove()
        folder = None
        for i, v in self.plugins.items():
            if v == plugin:
                folder =  i
                break
        del self.plugins[folder]
        
        if self.debug:
            print(Fore.GREEN + "Plugin \"" + plugin.configData["visualName"] + "\" was successfully removed." + Style.RESET_ALL)
    
    def cleanPlugins(self):
        if self.debug:
            print(Fore.BLUE + "Cleanign plugins." + Style.RESET_ALL)

        toRemove = []
        for plugin in self.plugins.values():
            if not plugin.loaded or not plugin.started:
                toRemove.append(plugin)

        for plugin in toRemove:
            self._removePlugin(plugin)
        
                
    

    