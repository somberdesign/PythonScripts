from sys import exit, path
from bs4 import BeautifulSoup

# this is a test

path.append(r'c:\users\rgw3\PythonScripts\Logger')
import Logger2

from os.path import dirname, isfile, join, realpath
from requests import get
import typing
from yaml import safe_load, YAMLError
from re import IGNORECASE, search, sub

TAB_CLASS_TITLE:str = 'shui-dt-column__title'
TAB_CLASS_TIMEREMAINING:str = 'shui-dt-column__timeRemaining'

MINUTE_CUTOFF = 26*60

THIS_FILE_PATH = dirname(realpath(__file__))
INPUT_FILE_PATH = r'C:\temp\ebay.html'
OUTPUT_FILE_PATH = r'C:\temp\ebayScrapeActiveListings_output.txt'
PREVIOUS_ITEM_PATH = r'C:\temp\ebayScrapeActiveListings_previous.txt'
STRINGS_TO_REMOVE = ['See condition descriptionBuy It Now', 'suitable for reading and handling', 'detailed condition description', 'by', 'screener', 'various']

countBucket = { 'BadString': 0, 'TimeRejected': 0 }
logger = None
ebayUrl:str = str()

def create_item_text(inString:str) -> str:
    global countBucket
    return_val:str = str()
    searchData:typing.List = [('cd', 'cd'), ('cassette tape', 'ct'), ('cgc', 'cb')]
    remove_year = True # remove date from string
    is_comic_book = search(r'\b#\d{1,3}\b', inString) is not None

    # ignore items that contain any of these words
    for word in ['ItemSort', 'TitleSort']:
        if word.lower() in inString.lower(): 
            countBucket['BadString'] += 1
            return str()

    # graded comics
    # ex: "Nightmask 2 Dec 1986 CGC 94"
    if 'cgc' in inString.lower():
        remove_year = False
        findLocation = inString.lower().find('cgc')
        return f'cb {inString[:findLocation]}'


    # if able to identify type of item being sold, 
    # add the appropriate prefix and delete everthing after the keyword
    for item in searchData:
        findLocation = inString.lower().find(' (' + item[0])
        if findLocation == -1: continue

        return_val = f'{item[1]} {inString[:findLocation]}'
        break
        
    # default to dvd or complete string
    if len(return_val) == 0:
        findLocation = inString.lower().find(' (')
        if findLocation != -1:
            return_val = f'{inString[:findLocation]}'
        else:
            return_val = inString

    # strip non-alpanumeric chars
    return_val = sub(r'[^A-Za-z0-9 ]+', str(), return_val)

    # replace "season x" with "sx"
    return_val = sub(r'(season )(/n)', 's\2', return_val, flags=IGNORECASE)

    # replace "volume x" with "vx"
    return_val = sub(r'(volume )(/n)', 'v\2', return_val, flags=IGNORECASE)
    return_val = sub(r'(vol )(/n)', 'v\2', return_val, flags=IGNORECASE)

    #remove region
    return_val = sub('region \n', '', return_val, flags=IGNORECASE)

    # remove date
    if remove_year and not is_comic_book:
        return_val = sub(r'\b\d{4}\b', '', return_val, flags=IGNORECASE)

    # remove strings that are not relevant to the search
    for string in STRINGS_TO_REMOVE:
        if return_val.lower().startswith(string.lower() + ' '):
            return_val = sub(string + ' ', '', return_val, flags=IGNORECASE)

        if return_val.lower().endswith(' ' + string.lower()):
            return_val = sub(' ' + string, '', return_val, flags=IGNORECASE)

        if return_val.lower().find(' ' + string.lower() + ' ') != -1:
            return_val = sub(' ' + string + ' ', ' ', return_val, flags=IGNORECASE)

    # remove doubled spaces (this one is last)
    return_val = return_val.replace('  ', ' ')

    return return_val.strip()

def GetConfigValues() -> bool:
    returnVal:bool = True
    configFilePath = join(THIS_FILE_PATH, "eBayScraper.yaml")
    fallbackLogfile = join(THIS_FILE_PATH, "eBayScrapeActiveListing.log")
    yamlData = None

    with open(configFilePath) as stream:
        try:
            yamlData = safe_load(stream)

        except YAMLError as exc:
            print(exc)
            returnVal = False
        
    logfilePath:str = str()
    if 'eBayScrapeActiveListings' in yamlData and 'logfile' in yamlData['eBayScrapeActiveListings']: # type: ignore
        logfilePath = yamlData['eBayScrapeActiveListings']['logfile'] # type: ignore
    else:
        print(f'ERROR: unable to find "eBayScrapeActiveListings\\logfile" in config file {configFilePath}. Using fallback file {fallbackLogfile}')
        logfilePath = fallbackLogfile
        returnVal = False

    if 'eBayScrapeActiveListings' in yamlData and 'url' in yamlData['eBayScrapeActiveListings']: # type: ignore
        global ebayUrl
        ebayUrl = yamlData['eBayScrapeActiveListings']['url'] # type: ignore
    else:
        print(f'ERROR: unable to find "eBayScrapeActiveListings\\url" in config file {configFilePath}')
        logfilePath = fallbackLogfile
        returnVal = False

    print(f'Logging to file {logfilePath}')
    Logger2.SetLogfilePath(logfilePath)
    Logger2.AddInfo('Started run')

    return returnVal

def make_soup_file(filename:str) -> BeautifulSoup | None:

    filecontents:str = str()
    try:
        with open(filename) as f:
            filecontents = f.read()        
    except Exception as ex:
        Logger2.AddError(f'Unable to read input file {INPUT_FILE_PATH}. {ex}')
        print('pause')
        input()
        exit(1)

    return BeautifulSoup(filecontents, 'html.parser')

def make_soup_url(url:str) -> BeautifulSoup | None:
    r = get(url)
    if r.status_code != 200:
        print('Failed to get data: ', r.status_code)
        return None
    
    return BeautifulSoup(r.text, 'html.parser')

def removeYesterday(inList:list) -> list:
    # remove items that appear in yesterday's file
    
    # read items from file
    previousItems = []
    try:
        with open(PREVIOUS_ITEM_PATH, 'r') as yesterday:
            for item in yesterday:
                previousItems.append(item.strip())
    except Exception as ex:
        Logger2.AddError(f"Error opening yesterday's items file {PREVIOUS_ITEM_PATH}. {ex}")

    # remove them from returnval if they match
    if len(previousItems) > 0:
        for item in previousItems:
            if item.strip() in inList:
                inList.remove(item.strip())
    
    # write new yeserday file
    try:
        with open(PREVIOUS_ITEM_PATH, 'w') as yesterday:
            for item in inList:
                yesterday.write(item + '\n')
    except Exception as ex:
        Logger2.AddError(f'Unable to write items to yesterday file {PREVIOUS_ITEM_PATH}. {ex}')

    return inList

def TimeLeftToMinutes(instr:str) -> int:
    # instr looks like this: "1d 23h 41m"

    returnVal:int = 0
    minuteLookup:dict = {'d':24*60, 'h':60, 'm':1}

    parts = instr.split()
    for part in parts:
        if part[:-1].isnumeric() and part[-1:] in ['d', 'h', 'm']:
            returnVal += int(part[:-1]) * minuteLookup[part[-1:]]

    return returnVal



if __name__ == '__main__':
    
    GetConfigValues()

    soup:BeautifulSoup | None = make_soup_file(INPUT_FILE_PATH)
    tagTitles = soup.select("." + TAB_CLASS_TITLE)

    outputItems = []
    for titleElement in tagTitles:

        # ignore item if it doesn't expire within about a day
        timeRemainingElement = titleElement.find_next('td', class_=TAB_CLASS_TIMEREMAINING)
        minutesLeft = TimeLeftToMinutes(timeRemainingElement.text)
        if minutesLeft > MINUTE_CUTOFF: 
            countBucket['TimeRejected'] += 1
            continue

        cleanItem:str = create_item_text(titleElement.text)
        if cleanItem:
            outputItems.append(cleanItem)

    outputCount = len(outputItems)

    
    # get rid of yesterday's items
    outputItems = removeYesterday(outputItems)
    yesterdayCount = outputCount - len(outputItems)

    try:
        with open(OUTPUT_FILE_PATH, 'w') as f:
            for item in outputItems:
                f.write(item + '\n')
        
    except Exception as ex:
        Logger2.AddError(f'Error writing file {OUTPUT_FILE_PATH}. {ex}')

    Logger2.AddInfo(f"Read {len(tagTitles) - 1 - countBucket['BadString']} listings\n{countBucket['TimeRejected']} don't expire today\n{yesterdayCount} appeared yesterday")

    input('Pause')

