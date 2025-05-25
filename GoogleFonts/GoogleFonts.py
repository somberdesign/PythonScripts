from os import environ, path
from logging import exception as loggingException
from yaml import safe_load
from requests import get
from typing import Dict
from easygui import msgbox
from json import load, loads, dump
from datetime import datetime

GOOGLE_FONT_REQUEST_URI:str = f'https://www.googleapis.com/webfonts/v1/webfonts?key='
SUCCESS_RESPONSE:int = 200
FALLBACK_PYTHONSCRIPTS_DIRECTORY:str = r'C:\Users\rgw3\PythonScripts' + '\\'
CACHE_FILE_PATH:str = path.join(r'c:\temp\google_fonts_cache_file.json')
CACHE_FILE_MAX_AGE:int = 30 * 24 * 60 * 60

def GetGoogleFontData() -> Dict[str, object] | None:

    def LogMessage(message:str) -> None:
        loggingException(message)
        msgbox(message)

    def WriteCacheFile() -> bool:

        pythonscriptsPath:str = FALLBACK_PYTHONSCRIPTS_DIRECTORY
        try:
            pythonscriptsPath = environ['PYTHONSCRIPTS']
        except Exception as ex:
            LogMessage(f'GoogleFonts.py: Error reading environment variable PYTHONSCRIPTS. {ex}')

        secretsPath:str = path.join(pythonscriptsPath, 'Secrets.yaml')
        googleApiKey:str = str()

        # msgbox(f'{secretsPath=}')
        if not path.isfile(secretsPath):
            LogMessage(f'GoogleFonts.py: can\'t find Secrets.yaml at path {secretsPath}')
            return False

        
        try:
            with open(secretsPath, 'r') as file:
                myYaml = safe_load(file)
                googleApiKey = myYaml['google-api-keys']['manage-sheets']['value']
        except Exception:
            LogMessage(f'GoogleFonts.py: Error reading api key from {secretsPath}')
            return False

        fontdata = get(f'{GOOGLE_FONT_REQUEST_URI}{googleApiKey}')
        
        if not fontdata.status_code == SUCCESS_RESPONSE:
            LogMessage(f'GoogleFonts.py: Error reading font names. ({fontdata.reason})')
            return False
        
        jsondata = loads(fontdata.content)
        
        try:
            with open(CACHE_FILE_PATH, 'w') as f:
                dump(jsondata, f)
        except Exception as ex:
            LogMessage(f'Error writing cache file {ex}')
            return False
        
        return True

    # re-write the cache file if it's missing or old
    if not path.isfile(CACHE_FILE_PATH) or datetime.now().timestamp() - path.getmtime(CACHE_FILE_PATH) > CACHE_FILE_MAX_AGE:
        WriteCacheFile()
    
    fontdata:str = str()
    
    try:
        with open(CACHE_FILE_PATH, 'r') as f:
            fontdata = load(f)

    except Exception as ex:
        LogMessage(f'Error reading cache file at {CACHE_FILE_PATH}. {ex}')
        return None

    return fontdata # type: ignore



if __name__ == '__main__':

    GetGoogleFontData()




