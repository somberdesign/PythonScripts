import csv
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

CREDENTIALS_PATH = r'..\Manage Sheets-b5896c4ab53e.json'
CSV_DIR = '.\Csv'
SPREADSHEET_IDS = [
	['2014', '1PD2jKdjtYYgkEeNGvagdpj651ZxpuRjaXYs52cZlrXw']
]

if __name__ == "__main__":

	# delete existing CSVs
	for f in glob.glob(os.path.join(CSV_DIR, '*.csv')):
		os.remove(f)

	scope = ['https://spreadsheets.google.com/feeds']
	credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)

	for spreadsheet_id in SPREADSHEET_IDS:
		docid = spreadsheet_id[1]
		client = gspread.authorize(credentials)
		spreadsheet = client.open_by_key(docid)
		for i, worksheet in enumerate(spreadsheet.worksheets()):
			filename = docid + '-worksheet' + str(i) + '.csv'
			with open(os.path.join(CSV_DIR, filename), 'w') as f:
				writer = csv.writer(f)
				writer.writerows(worksheet.get_all_values())