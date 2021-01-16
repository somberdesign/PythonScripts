import sys
import csv
import glob
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import os
import shutil

sys.path.insert(1, r'../DownloadCsv')
import DownloadCsv

SPREADSHEET_IDS = [
	('Toxic Tribulations', '1DC3uQdeKlIJMbGvJijwTA6AbDN7QjYu5B-ooawjaITc'),
	('Tomb of the Science Wizard', '18W1Kz9ch-Xy729ap6OHkRTHGStJ8pKwiDpLJSRoC6KU')
]
WORKSHEET_POSITIONS = None

if __name__ == "__main__":

	for spreadsheet_id in SPREADSHEET_IDS:

		print(f'\nReading {spreadsheet_id[0]}')
		
		params = DownloadCsv.DownloadGoogleCsv.NewInstanceParameters(spreadsheet_id, WORKSHEET_POSITIONS)
		params.FirstDataLine = 4

		downloadGoogleCsv = DownloadCsv.DownloadGoogleCsv(params)
		csvs = downloadGoogleCsv.DownloadCsvs()

		for c in csvs:
			print(c)
