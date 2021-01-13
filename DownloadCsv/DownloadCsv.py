import csv
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import shutil

CREDENTIALS_PATH = r'..\Manage Sheets-b5896c4ab53e.json'
FIRST_DATA_LINE = 4
WORKBOOK_SCOPE = ['https://spreadsheets.google.com/feeds']

CsvDirectory = ''
FirstDataLine = 1
SpreadsheetId = ()
WorksheetPositions = []

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

		self.CsvDirectory = f'Csv_{newInstanceParameters.SpreadsheetId[1]}'
		self.FirstDataLine = newInstanceParameters.FirstDataLine
		self.SpreadsheetId = newInstanceParameters.SpreadsheetId
		self.WorksheetPositions = newInstanceParameters.WorksheetPositions


	def DownloadCsvs(self):
		# delete old CSVs
		if os.path.isdir(self.CsvDirectory):
			print(f'Deleting directory: {self.CsvDirectory}')
			
			try:
				shutil.rmtree(self.CsvDirectory)
			except Exception as ex:
				print(f'Unable to delete directory {self.CsvDirectory}. Exiting. {ex}')
				return

		os.mkdir(self.CsvDirectory)

		credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, WORKBOOK_SCOPE)
		docid = self.SpreadsheetId[1]
		client = gspread.authorize(credentials)

		print(f'Reading workbook: {self.SpreadsheetId[0]}')
		spreadsheet = client.open_by_key(docid)
		
		# save each worksheet as a csv
		sheetCount = [0, 0]
		for i, worksheet in enumerate(spreadsheet.worksheets()):

			if i >= len(self.WorksheetPositions):
				sheetCount[1] += 1
				continue

			sheetCount[0] += 1
			print(f'Worksheet {i}: {self.WorksheetPositions[i][1]}', end='')

			filename = self.SpreadsheetId[0] + '-worksheet-' + str(self.WorksheetPositions[i][1]).replace(' ', '') + '.csv'
			filenameFullPath = os.path.join(self.CsvDirectory, filename)
			
			with open(filenameFullPath, 'w') as f:
				print(f', writing file {filename}')
				writer = csv.writer(f)
				writer.writerows(worksheet.get_all_values())

		print(f'Read the first {sheetCount[0]} sheets and skipped the last {sheetCount[1]}')

		# remove blank lines
		csvPaths = []
		print('Removing blank lines...')
		for f in os.listdir(self.CsvDirectory):
			if os.path.isdir(f):
				continue

			lines = []
			fullpath = os.path.join(self.CsvDirectory, f)
			csvPaths.append(os.path.abspath(fullpath))
			print(f'  {fullpath}')
			
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


# if __name__ == '__main__':

# 	SPREADSHEET_ID = ('Sales', '1PD2jKdjtYYgkEeNGvagdpj651ZxpuRjaXYs52cZlrXw')

# 	WORKSHEET_POSITIONS = [ # position of sheets within workbook Sales. eBay Sales sheets must be first
# 		(0, "DVD Sales 2020"),
# 		(1, "DVD Sales 2019"),
# 		(2, "DVD Sales 2018"),
# 		(3, "DVD Sales 2017"),
# 		(4, "DVD Sales 2016"),
# 		(5, "DVD Sales 2015"),
# 		(6, "DVD Sales 2014"),
# 	]

# 	params = DownloadGoogleCsv.NewInstanceParameters(SPREADSHEET_ID, WORKSHEET_POSITIONS)
# 	params.FirstDataLine = 4

# 	downloadGoogleCsv = DownloadGoogleCsv(params)
# 	csvs = downloadGoogleCsv.DownloadCsvs()

# 	for c in csvs:
# 		print(c)