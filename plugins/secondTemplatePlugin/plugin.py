# Do not remove

from modules.PluginManager.Plugin import Plugin 
###

class Plugin(Plugin):
    def onLoad(self):
        pass

    def start(self):
        pass

    def testFunction(self):
        print("Test function from secondTemplatePlugin")

    def onRemove(self):
        pass