import csv
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import shutil

CREDENTIALS_PATH = r'..\Manage Sheets-b5896c4ab53e.json'
FIRST_DATA_LINE = 4
WORKBOOK_SCOPE = ['https://spreadsheets.google.com/feeds']
SPREADSHEET_IDS = [
	['Sales', '1PD2jKdjtYYgkEeNGvagdpj651ZxpuRjaXYs52cZlrXw']
]
WORKSHEET_POSITIONS = [ # position of sheets within workbook Sales. eBay Sales sheets must be first
	[0, "DVD Sales 2020"],
	[1, "DVD Sales 2019"],
	[2, "DVD Sales 2018"],
	[3, "DVD Sales 2017"],
	[4, "DVD Sales 2016"],
	[5, "DVD Sales 2015"],
	[6, "DVD Sales 2014"],
]

if __name__ == "__main__":

	credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, WORKBOOK_SCOPE)

	for spreadsheet_id in SPREADSHEET_IDS:

		# delete old CSVs
		csvDirectory = f'Csv_{spreadsheet_id[0]}'
		if os.path.isdir(csvDirectory):
			print(f'Deleting directory: {csvDirectory}')
			
			try:
				shutil.rmtree(csvDirectory)
			except Exception as ex:
				print(f'Unable to delete directory {csvDirectory}. Skipping workbook. {ex}')
				continue

		os.mkdir(csvDirectory)

		docid = spreadsheet_id[1]
		client = gspread.authorize(credentials)

		print(f'Reading workbook: {spreadsheet_id[0]}')
		spreadsheet = client.open_by_key(docid)
		
		# save each worksheet as a csv
		sheetCount = [0, 0]
		for i, worksheet in enumerate(spreadsheet.worksheets()):

			if i >= len(WORKSHEET_POSITIONS):
				sheetCount[1] += 1
				continue

			sheetCount[0] += 1
			print(f'Worksheet {i}: {WORKSHEET_POSITIONS[i][1]}')

			filename = spreadsheet_id[0] + '-worksheet-' + WORKSHEET_POSITIONS[i][1].replace(' ', '') + '.csv'
			with open(os.path.join(csvDirectory, filename), 'w') as f:
				print(f'Writing file: {filename}')
				writer = csv.writer(f)
				writer.writerows(worksheet.get_all_values())

		print(f'Read the first {sheetCount[0]} sheets and skipped the last {sheetCount[1]}')

		# remove blank lines
		print('Removing blank lines...')
		for f in os.listdir(csvDirectory):
			if os.path.isdir(f):
				continue

			lines = []
			fullpath = os.path.join(csvDirectory,f)
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
