import os
from ..jsonFunctions import getJsonData

class Plugin:
    def __init__(self, API):
        self.API = API
        self.loaded = False
        self.started = False

    def init(self):
        self.configData = getJsonData(os.path.join(self.currentPath, 'config.json'))

    def cleanUp(self):
        self.loaded = False