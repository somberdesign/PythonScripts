from bs4 import BeautifulSoup
from Logger import Logger2
from os.path import dirname, join, realpath
from requests import get
from yaml import safe_load, YAMLError

THIS_FILE_PATH = dirname(realpath(__file__))
logger = None
ebayUrl:str = str()


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

    
    Logger2.SetLogfilePath(logfilePath)
    Logger2.AddInfo('Started run')

    return returnVal

def make_soup(url: str) -> BeautifulSoup | None:
    r = get(url)
    if r.status_code != 200:
        print('Failed to get data: ', r.status_code)
        return None
    
    return BeautifulSoup(r.text, 'html.parser')

if __name__ == '__main__':
    GetConfigValues()
    soup = make_soup(ebayUrl)
    print(soup.text)
    pass


