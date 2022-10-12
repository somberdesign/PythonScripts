
from datetime import date
from glob import glob
from os import path

ALBUM_DIR = r'h:\Music\Albums'
OUTPUT_FILE = r'\Users\Bob\PythonScripts\SearchToBrowser\AlbumList.txt'


albumlist = []
for dir in glob(path.join(ALBUM_DIR, '*', '*')):
	if not path.isdir(dir):	continue
	albumlist.append(dir.split(path.sep)[dir.count(path.sep)])

albumlist = sorted(albumlist, key=str.casefold)

with open(OUTPUT_FILE, 'w') as f:
    f.write(f'{date.today()}\n')
    f.write(f'This file created by {__file__}\n')
    f.write(f'Wrote {len(albumlist)} items\n\n')
    for line in albumlist:
        f.write(f"{line}\n")





