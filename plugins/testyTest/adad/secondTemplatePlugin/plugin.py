# Do not remove
from modules.PluginManager.Plugin import Plugin 
###

class Plugin(Plugin):
    def onLoad(self):
        pass

    def start(self):
        self.API.changePluginOptions(self.API.getPlugin("secondTemplatePlugin"), "option2", {"value": "Option 2"})
    
    def optionsChanged(self, optionName, optionArgs):
        print(optionName, optionArgs)

    def testFunction(self):
        print("Test function from secondTemplatePlugin")

    def onRemove(self):
        pass