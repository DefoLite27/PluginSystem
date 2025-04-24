import json5

def getJsonData(filePath) -> dict:
    data = None
    with open(filePath, 'r') as file:
        data = json5.load(file)

    return data

def setJsonData(filePath, data) -> None:
    with open(filePath, 'w') as file:
        json5.dump(data, file, indent=4)