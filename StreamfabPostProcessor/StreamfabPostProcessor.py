from os import getcwd, path, walk
from glob import glob

files = [y for x in walk(getcwd()) for y in glob(path.join(x[0], '*.mp4'))]

for f in files:
    print(f)
    

