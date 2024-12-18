from os import getcwd, path, rename, sep, walk
from glob import glob
from string import punctuation

class filenameObject():
    def __init__(self, currentName = ""):
        self.currentName = currentName
        self.targetName = currentName


def ReplaceChars(filename):
    newFilename = str()        
    baseFilename = path.splitext(path.basename(filename))[0]

    for i in range(len(baseFilename)):
        if baseFilename[i] not in punctuation + " ": # no change if it's a good char
            newFilename += baseFilename[i]
            continue
        if baseFilename[i+1] in [' ', '.', sep]: # remove the char if it's at the end of a directory or file name
            continue
        newFilename += "_"

    return path.join(path.dirname(filename), newFilename + path.splitext(filename)[1])

        

def Main():
    filenameObjects = []
    readFiles = [y for x in walk(getcwd()) for y in glob(path.join(x[0], '*.mp4'))]
    
    # populate list of filenameObjects
    for currentFilename in readFiles:
        filenameObjects.append(filenameObject(currentFilename))

    for o in filenameObjects:
        o.targetName = ReplaceChars(o.targetName)
        
    for o in filenameObjects:
        if (o.currentName == o.targetName):
            print(f'Skipped: no change ({path.basename(o.targetName)})')
            continue

        try:
            rename(o.currentName, o.targetName)
            print(f'Success: {o.targetName}')
        except Exception as ex:
            print(f'Error renaming file {o.currentName}. {ex}')

    

if __name__ == '__main__':
    Main()
    input('Done')