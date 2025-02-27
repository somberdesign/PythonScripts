from os import getcwd, listdir, rename
from os.path import isdir
from re import compile
from sys import argv

# 2025-02-23 Use on a directory full of series episodes with the
# wrong episode number. This replaces the existing episode number with an
# incrementing number that starts with 1. The existing filenames must
# sort by name in the desired order.
#
# Example filename: Three_s_Company_S07E144_Going_to_Pot.mp4


DEBUG = False

if __name__ == '__main__':

    if DEBUG: print('DEBUG enabled')

    # check for dir on command line
    targetDir = getcwd()
    argc = len(argv)
    if argc > 1 and isdir(argv[1]):
        targetDir = argv[1]

    # loop over files
    counter = 0
    for currentFilename in listdir(targetDir):
        counter += 1
        
        # sample: Three_s_Company_S07E144_Going_to_Pot.mp4
        p = compile('S[0-9]{2}E[0-9].')
        p.match(currentFilename)
        m = p.search(currentFilename)
        span = m.span()
        newFilename = currentFilename[0:span[0]+3] + f'E{counter:02}' + currentFilename[span[1]+1:]
        
        print(f'{currentFilename} --> {newFilename}')
        if not DEBUG:
            try:
                rename(currentFilename, newFilename)
            except Exception as ex:
                print(f'ERROR renaming file {currentFilename}. {ex}')