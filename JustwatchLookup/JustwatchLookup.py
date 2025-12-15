

import Logger2
from sys import argv, exit
from webbrowser import open as webopen
from urllib.parse import quote_plus

LOGFILE_PATH = r'c:\Logs\JustwatchLookup.log'
Logger2.SetLogfilePath(LOGFILE_PATH)


if __name__ == '__main__':

    # get input filename from command line
    if len(argv) < 2:
        print('Usage: eBayScrapeActiveListings.py <input filename>')
        exit(1)
    INPUT_FILE_PATH = argv[1] 

    # read input file
    lines = []
    try:
        with open(INPUT_FILE_PATH, 'r') as f:
            lines = f.readlines()
    except Exception as ex:
        Logger2.AddError(f'Unable to read input file {INPUT_FILE_PATH}. {ex}')
        exit(1) 

    # process each line
    itemCount = 0
    for line in lines:
        line = line.strip()
        if line == '' or line.startswith('#'):
            continue

        searchTerm = quote_plus(line.split('#')[0].strip()) # ignore everything after a '#'
        url = f'https://www.justwatch.com/us/search?q={searchTerm}'
        webopen(url)
        itemCount += 1

    Logger2.AddInfo(f'Finished run. Opened {itemCount} Justwatch search pages.')