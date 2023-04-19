
from datetime import date, datetime
from genericpath import isfile
from glob import glob
from os import path, stat
import time

ALBUM_DIR = r'h:\Media\Music\Albums'
ALBUM_DIR_CACHE = r'\Users\Bob\PythonScripts\FileList\.albumlistcache'
OUTPUT_FILE = r'\Users\Bob\PythonScripts\SearchToBrowser\AlbumList.txt'
HEADER_LINE_COUNT = 4



def CreateCacheFile():
	albumlist = []
	for dir in glob(path.join(ALBUM_DIR, '*', '*')):
		if not path.isdir(dir):	continue
		albumlist.append(dir.split(path.sep)[dir.count(path.sep)])
	albumlist = sorted(albumlist, key=str.casefold)

	with open(ALBUM_DIR_CACHE, 'w') as f:
		f.write(f'# {str(datetime.now())[0:16]} This file created by {__file__}\n')
		for s in albumlist:
			cleanStr = ''.join(char for char in s if ord(char) < 128) # strip weird characters
			f.write(cleanStr + '\n')

if (
	not path.isfile(ALBUM_DIR_CACHE) or
	path.isfile(ALBUM_DIR_CACHE) and (time.time() - path.getmtime(ALBUM_DIR_CACHE)) > (60 * 60 * 1)
):
	CreateCacheFile()

albumlist = None
with open(ALBUM_DIR_CACHE, 'r') as f:
	albumlist = f.read().splitlines()


with open(OUTPUT_FILE, 'w') as f:
	f.write(f'{date.today()}\n')
	f.write(f'This file created by {__file__}\n')
	f.write(f'Wrote {len(albumlist) - HEADER_LINE_COUNT} items\n\n')
	for line in albumlist:
		if line[0] == '#':
			continue
		f.write(f"{line}\n")







