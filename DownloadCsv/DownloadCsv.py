import csv
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import re
import shutil
import unicodedata

CREDENTIALS_PATH = r'..\Manage Sheets-b5896c4ab53e.json'
FIRST_DATA_LINE = 4
WORKBOOK_SCOPE = ['https://spreadsheets.google.com/feeds']

CsvDirectory = ''
FirstDataLine = 1
SpreadsheetId = ()
WorksheetPositions: list = []

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')
	
class DownloadGoogleCsv:
	
	CsvDirectory: str = ''
	FirstDataLine: int = 1
	SpreadsheetId: tuple = ()
	WorksheetPositions: list = []

	class NewInstanceParameters:
		
		FirstDataLine = 1
		
		def __init__(self, spreadsheetId, worksheetPositions):
			self.SpreadsheetId = spreadsheetId
			self.WorksheetPositions = worksheetPositions



	def __init__(self, newInstanceParameters):

		self.CsvDirectory = f'CsvFiles_{newInstanceParameters.SpreadsheetId[1]}'
		self.FirstDataLine = newInstanceParameters.FirstDataLine
		self.SpreadsheetId = newInstanceParameters.SpreadsheetId
		self.WorksheetPositions = newInstanceParameters.WorksheetPositions


	def DownloadCsvs(self, targetDir: str):
		if len(targetDir) == 0:
			print('DownloadCsvs(): targetDir must have a value')
			return None

		if targetDir == '.':
			print('DownloadCsvs(): targetDir cannot be current directory')
			return None

		self.CsvDirectory = targetDir

		if not os.path.isdir(self.CsvDirectory):
			os.mkdir(self.CsvDirectory)

		credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, WORKBOOK_SCOPE)
		docid = self.SpreadsheetId[1]
		client = gspread.authorize(credentials)

		print(f'Reading workbook: {self.SpreadsheetId[0]}')
		spreadsheet = client.open_by_key(docid)
		
		# save each worksheet as a csv
		sheetCount = [0, 0]  # processed, skipped
		for i, worksheet in enumerate(spreadsheet.worksheets()):

			sheetName = worksheet.title
			if self.WorksheetPositions is not None and i >= len(self.WorksheetPositions):
				sheetCount[1] += 1
				continue

			sheetCount[0] += 1
			print(f'Worksheet {i}: {sheetName}', end='')

			# filename has three parts: <int>_<title>_<sheetname>.csv
			filename = str(i) + '_' + slugify(spreadsheet.title) + '_' + str(sheetName).replace(' ', '') + '.csv'
			filenameFullPath = os.path.join(self.CsvDirectory, filename)
			
			with open(filenameFullPath, 'w') as f:
				print(f', writing file {filename}')
				for line in worksheet.get_all_values():
					stringToWrite = ''
					for item in line:
						stringToWrite += '"' + item.replace('"', '\'') + '",'
					stringToWrite = stringToWrite[:-1]
					f.write(f'{stringToWrite}\n')


		print(f'Read the first {sheetCount[0]} sheets and skipped the last {sheetCount[1]}')

		# remove blank lines
		csvPaths = []
		print('Removing blank lines...')
		for f in os.listdir(self.CsvDirectory):
			if os.path.isdir(f):
				continue

			lines = []
			fullpath = os.path.join(self.CsvDirectory, f)
			absPath = os.path.abspath(fullpath)
			# print(f'absPath={absPath}')
			csvPaths.append(absPath)
			
			try:
				with open(fullpath, 'r') as original:
					lines = original.readlines()
			except Exception as ex:
				print(f'Error reading {fullpath}. {ex}')
				continue

			try:
				with open(fullpath, 'w') as modified:
					lineCounter = 0
					for l in lines:
						
						lineCounter += 1
						if (
							(lineCounter > FIRST_DATA_LINE and l[0] == ',') # skip line if it doesn't contain data
							or l.isspace()
						):
							continue
						
						modified.write(l)

			except Exception as ex:
				print(f'Error writing {fullpath}. {ex}')
				continue

		return csvPaths


