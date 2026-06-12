from sys import exit, path, flags
from bs4 import BeautifulSoup

# this is a test

path.append(r'c:\users\rgw3\PythonScripts\Logger')
import Logger2

from os.path import dirname, isfile, join, realpath
from requests import get
import typing
from yaml import safe_load, YAMLError
from re import IGNORECASE, search, sub
from sys import float_info

TAB_CLASS_CURRENT_PRICE:str = 'col-price__current'
TAB_CLASS_TITLE:str = 'shui-dt-column__title'
TAB_CLASS_TIMEREMAINING:str = 'shui-dt-column__timeRemaining'


MINUTE_CUTOFF = 26*60

INPUT_FILE_PATH = r'C:\temp\ebay.html'
OUTPUT_FILE_PATH = r'C:\temp\ebayScrapeActiveListings_output.txt'
POSITIONAL_NUMBERS = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth']
PREVIOUS_ITEM_PATH = r'C:\temp\ebayScrapeActiveListings_previous.txt'
STRINGS_TO_REMOVE = ['See condition description', 'Buy It Now', 'suitable for reading and handling', 'detailed condition description', 'watched once']
THIS_FILE_PATH = dirname(realpath(__file__))
WORDS_TO_REMOVE = ['by', 'screener', 'various']

countBucket = { 'BadString': 0, 'TimeRejected': 0 , 'CheapComic': 0}
# logger = None
ebayUrl:str = str()

def create_item_text(inString:str, current_price:str) -> str:
    global countBucket

    def contains_bracketed_grade(inString:str) -> bool:
        cgc_grade_abbreviations:typing.List[str] = ['NM/M', 'NM+', 'NM', 'NM-', 'VF/NM', 'VF+', 'VF', 'VF-', 'FN/VF', 'FN', 'FN-', 'VG/FN', 'VG+', 'VG', 'VG-', 'G/VG', 'G', 'G-', 'Fa/G', 'Fa', 'Poor']
        return any(f'[{grade}]' in inString for grade in cgc_grade_abbreviations)

    def remove_year(inString:str) -> bool:
        if search(r'\sbest of\s\d{4}', inString, flags=IGNORECASE) is not None:
            return False
        return True

    def replace_season_volume_strings(inString:str) -> str:
        return_val:str = inString

        # replace "season x" with "sx"
        for s in ['season', 'series']:
            return_val = sub(fr'({s})\s(\d)', r's\2', return_val, flags=IGNORECASE)

        # replace "volume x" with "vx"
        for v in ['volume', 'vol']:
            return_val = sub(fr'({v})\s(\d)', r'v\2', return_val, flags=IGNORECASE)

        # remove positional numbers if season or vol notation is present
        if search(r'[sv]\d', return_val, flags=IGNORECASE) is not None:
            for s in POSITIONAL_NUMBERS:
                return_val = sub(fr'({s})\s', str(), return_val, flags=IGNORECASE)

        return return_val
    
    ###########################################################################

    return_val:str = str()

    price = float_info.max
    try:
        price = float(sub(r'[^0-9.]', '', current_price))
    except ValueError:
        Logger2.AddInfo(f"Failed to parse price '{current_price}' for item '{inString}'")

    comic_book_specific_strings:typing.List[str] = ['suitable for reading and handling', 'detailed condition description']
    is_comic_book = (
            search(r'\s#\d{1,3}\s', inString) is not None
            or contains_bracketed_grade(inString)
            or any(s in comic_book_specific_strings for s in inString.lower())
    )

    is_cgc_comic_book = 'cgc' in inString.lower()

    if is_comic_book and price < 10:
        countBucket['CheapComic'] += 1
        return str()

    # ignore items that contain any of these words
    for word in ['ItemSort', 'TitleSort']:
        if word.lower() in inString.lower(): 
            countBucket['BadString'] += 1
            return str()

    if is_comic_book:
        if is_cgc_comic_book : # graded comics ex: "Nightmask 2 Dec 1986 CGC 94"
            cgc_return_val = inString
            cgc_return_val = cgc_return_val.replace('#', '') # can't figure out how to put # signs on the url
            find_location = cgc_return_val.lower().find('cgc')
            return_val = f'cb {cgc_return_val[:find_location]}'
        else:
            find_location = inString.lower().find('[')
            return_val = f'cb {inString[:find_location]}' if find_location != -1 else inString

    # magazines
    if 'magazine' in inString.lower():
        return_val = f'mg {inString}'

    # if able to identify type of item being sold (cd or dvd),
    # add the appropriate prefix and delete everything after the keyword
    # comic books are taken care of above
    search_data:typing.List = [('cd', 'cd'), ('cassette tape', 'ct')]
    for item_type in search_data:
        find_location = inString.lower().find(' (' + item_type[0])
        if find_location == -1: continue

        return_val = f'{item_type[1]} {inString[:find_location]}'
        break
        
    # default to dvd or complete string
    if len(return_val) == 0:
        find_location = inString.lower().find(' (')
        if find_location != -1:
            return_val = f'{inString[:find_location]}'
        else:
            return_val = inString

    # remove ebay item numbers
    return_val = sub(r'\b\d{12}\b', '', return_val, flags=IGNORECASE)

    # strip non-alphanumeric chars
    return_val = sub(r'[^A-Za-z0-9 ]+', str(), return_val)

    # sx and vx
    replace_season_volume_strings(return_val)

    #remove region
    return_val = sub(r'region \n', '', return_val, flags=IGNORECASE)

    # remove year from string. primarily for cds and dvds.
    if remove_year and not is_comic_book:
        return_val = sub(r'\b\d{4}\b', '', return_val, flags=IGNORECASE)

    # remove strings that are not relevant to the search
    for string in STRINGS_TO_REMOVE:
        if return_val.lower().find(string.lower()) != -1:
            return_val = sub(string, ' ', return_val, flags=IGNORECASE)

    # words to remove
    for string in WORDS_TO_REMOVE:
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
    
    # write new yesterday file
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
        current_price_element = titleElement.find_next('div', class_=TAB_CLASS_CURRENT_PRICE)
        if minutesLeft > MINUTE_CUTOFF: 
            countBucket['TimeRejected'] += 1
            continue

        cleanItem:str = create_item_text(titleElement.text, current_price_element.text)
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

    message = f"""
        Read {len(tagTitles) - 1 - countBucket['BadString']} listings
        {len(outputItems)} good ones
        {countBucket['TimeRejected']} don't expire today
        {countBucket['CheapComic']} {'is a cheap comic' if countBucket['CheapComic'] == 1 else 'are cheap comics'}
        {yesterdayCount} appeared yesterday
    """
    Logger2.AddInfo(message)
    # Logger2.AddInfo(f"Read {len(tagTitles) - 1 - countBucket['BadString']} listings\n{len(outputItems)} good ones\n{countBucket['TimeRejected']} don't expire today\n{yesterdayCount} appeared yesterday")

    input('Pause')

