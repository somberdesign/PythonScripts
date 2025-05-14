
from os import path
from requests import get
from subprocess import call
from sys import exit
from urllib.parse import quote_plus

# 2025-05-09 Create a Movie Sales List
# see readme at ~\ReadSalesCsv\_readme.txt

class Constant:
    MSG_ERROR = 'e'
    MSG_INFO = 'i'
    MSG_WARNING = 'w'

    OUTPUT_DIR = r'E:\Users\bob\PythonScripts\ReadSalesCsv\Csv_Sales'
    OUTPUT_FILENAME = '11_Sales-DVDSales2025.csv'
    OUTPUT_FILEPATH =  path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    SHEET_NAME = 'DVD Sales 2025'
    SPREADSHEET_ID = '1PD2jKdjtYYgkEeNGvagdpj651ZxpuRjaXYs52cZlrXw'




def DownloadCsvSales() -> bool:
    url = f'https://docs.google.com/spreadsheets/d/{Constant.SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={quote_plus(Constant.SHEET_NAME)}'

    response = get(url)
    if response.status_code == 200:
        with open(Constant.OUTPUT_FILEPATH, 'wb') as f:
            f.write(response.content)
        HandleMessage(Constant.MSG_INFO, 'CSV file saved to: {}'.format(Constant.OUTPUT_FILEPATH))
        return True
    else:
        HandleMessage(Constant.MSG_ERROR, f'Error downloading Google Sheet: {response.status_code}')
        return False
    

def HandleMessage(messageType:str, displayText: str) -> None:
    displayMessageType = 'DEFAULT'
    match messageType:
        case Constant.MSG_ERROR:
            displayMessageType = 'ERROR'
        case Constant.MSG_INFO:
            displayMessageType = 'INFO'
        case Constant.MSG_WARNING:
            displayMessageType = 'WARNING'
        
    print(f'==  {displayMessageType}: {displayText}')


if __name__ == "__main__":

    oldOutputFileSize = path.getsize(Constant.OUTPUT_FILEPATH) if path.isfile(Constant.OUTPUT_FILEPATH) else 0

    # 1. Download as CSV any Sales sheets that have changed. Save them in dir ~\ReadSalesCsv\Csv_Sales. 
    #   ..Change the filename to match the following format: 0_Sales-DVDSales2021.csv. 
    if not DownloadCsvSales():
        HandleMessage(Constant.MSG_ERROR, f'Error downloading csv')
        exit(1)

    newOutputFileSize = path.getsize(Constant.OUTPUT_FILEPATH)
    if newOutputFileSize <= oldOutputFileSize:
        HandleMessage(Constant.MSG_WARNING, f'New file size ({newOutputFileSize}) is not larger than the old one ({oldOutputFileSize})')

    
    
