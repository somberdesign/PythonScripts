import sys
import csv
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import shutil

sys.path.insert(1, r'../DownloadCsv')
import DownloadCsv

SPREADSHEET_IDS = [
	('Sales', '1PD2jKdjtYYgkEeNGvagdpj651ZxpuRjaXYs52cZlrXw')
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


	for spreadsheet_id in SPREADSHEET_IDS:

		params = DownloadCsv.DownloadGoogleCsv.NewInstanceParameters(spreadsheet_id, WORKSHEET_POSITIONS)
		params.FirstDataLine = 4

		downloadGoogleCsv = DownloadCsv.DownloadGoogleCsv(params)
		csvs = downloadGoogleCsv.DownloadCsvs()

		for c in csvs:
			print(c)
