
from datetime import date
from glob import glob
from os import path

ALBUM_DIR = r'h:\Music\Albums'

albumlist = []
for dir in glob(path.join(ALBUM_DIR, '*', '*')):
    albumlist.append(dir.split(path.sep)[dir.count(path.sep)])

albumlist = sorted(albumlist, key=str.casefold)

with open('albumlist.txt', 'w') as f:
    f.write(f'{date.today()}\n')
    f.write(f'This file created by {__file__}\n\n')
    for line in albumlist:
        f.write(f"{line}\n")





