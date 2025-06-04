# Do not remove

from modules.PluginManager.Plugin import Plugin 
###

class Plugin(Plugin):
    def onLoad(self):
        
        pass

    def start(self):
        self.API.getPlugin("secondTemplatePlugin").testFunction()

    def optionsChanged(self, optionName, optionArgs):
        pass
        #print(optionName, optionArgs)

    def onRemove(self):
        pass