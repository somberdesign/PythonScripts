from os import getcwd, path, rename, sep, walk
from glob import glob
from string import punctuation
from unidecode import unidecode
from titlecase import titlecase

class filenameObject():
    def __init__(self, currentName = ""):
        self.currentName = currentName
        self.targetName = currentName


def ReplaceChars(filename):
    REMOVE_CHARACTER_LIST = ["'"] # remove these characters instead of replacing them
    REPLACEMENT_CHAR = "_"
    newFilename = str()        
    baseFilename = titlecase(unidecode(path.splitext(path.basename(filename))[0]))

    for i in range(len(baseFilename)):
        
        # always remove these chars
        if baseFilename[i] in REMOVE_CHARACTER_LIST:
            continue

        # no change if it's a good char
        if baseFilename[i] not in punctuation + " ":
            newFilename += baseFilename[i]
            continue
        
        #####  All chars below here are punctuation chars ####

        # remove the char if it's at the end of a directory or file name
        if len(baseFilename) >= i+2 and baseFilename[i+1] in [' ', '.', sep]:
            continue

        # don't create double underscores
        if baseFilename[i-1] == REPLACEMENT_CHAR or (len(baseFilename) >= i+2 and baseFilename[i+1] == REPLACEMENT_CHAR):
            continue

        newFilename += REPLACEMENT_CHAR

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