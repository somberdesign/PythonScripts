import csv
import glob
import json
import sys
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import os
import shutil

sys.path.insert(1, r'../DownloadCsv')
import DownloadCsv

sys.path.insert(1, f'../DatabaseInterface')
import DatabaseInterface as db

sys.path.insert(1, r'../ManageCsv')
from ManageCsv import ReadCsv

DB_DATABASE_NAME = 'combatstats'
DB_HOST = 'mysql.robiii.dreamhosters.com'
DB_USER = 'marytm'

SECRETS_PATH = '../Secrets.json'
SECRETS_KEY = 'robiii_mysql_password'

dbPassword = ''
objectsPresentInDb = []


SPREADSHEET_IDS = [
	('Toxic Tribulations', '1DC3uQdeKlIJMbGvJijwTA6AbDN7QjYu5B-ooawjaITc'),
	('Tomb of the Science Wizard', '18W1Kz9ch-Xy729ap6OHkRTHGStJ8pKwiDpLJSRoC6KU')
]
WORKSHEET_POSITIONS = None


def DbGetCampaigns():
	dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
	interface = db.DatabaseInterface(dbParameters)

	return interface.GetResultSetFromProc('campaigns_get')


def DbInsertCampaign(campaignName: str):

	IDX_CAMPAIGN_NAME = 1

	if f'campaign_{campaignName}' in objectsPresentInDb:
		return True

	# one dataset in this result set
	getCampaignResults = DbGetCampaigns()
	if getCampaignResults is None or len(getCampaignResults) == 0:
		print(f'ERROR: can\'t get campaign names')
		return False
	
	campaignDataset = getCampaignResults[0]

	campaignNames = []
	for c in campaignDataset:
		campaignNames.append(c[IDX_CAMPAIGN_NAME])

	if campaignName in campaignNames:
		objectsPresentInDb.append(f'campaign_{campaignName}')
		return True

	dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
	interface = db.DatabaseInterface(dbParameters)
	interface.ExecuteProc('campaign_insert', [campaignName])

	objectsPresentInDb.append(f'campaign_{campaignName}')

	return True


def GetSpreadsheets():
	
	spreadsheetPaths = {}
	for spreadsheet_id in SPREADSHEET_IDS:

		print(f'\nReading {spreadsheet_id[0]}')
		
		params = DownloadCsv.DownloadGoogleCsv.NewInstanceParameters(spreadsheet_id, WORKSHEET_POSITIONS)
		params.FirstDataLine = 4

		downloadGoogleCsv = DownloadCsv.DownloadGoogleCsv(params)
		csvs = downloadGoogleCsv.DownloadCsvs()

		for c in csvs:
			
			# add campaign name to dictionary
			if not spreadsheet_id[0] in spreadsheetPaths:
				spreadsheetPaths[spreadsheet_id[0]] = []
			
			spreadsheetPaths[spreadsheet_id[0]].append(c)

	return spreadsheetPaths


def ReadConfiguration():
	global dbPassword

	# read file
	data = None
	try:
		with open(SECRETS_PATH) as json_file:
			data = json.load(json_file)
	except Exception as ex:
		print(f'Exception opening {SECRETS_PATH}: {ex}')
		return False

	if data is None:
		print(f'Failed to read {SECRETS_PATH}')
		return False

	if SECRETS_KEY not in data:
		print(f'Can\'t find key {SECRETS_KEY} in config file')
		return False

	dbPassword = data[SECRETS_KEY]

	return True 


def WriteSheetToDb(campaignName: str, spreadSheetPath: str):
	
	DbInsertCampaign(campaignName)

	csvLines = ReadCsv.Read(spreadSheetPath)
	a=1


if __name__ == "__main__":
	
	if not ReadConfiguration():
		print(f'ERROR: can\'t read configuration file {SECRETS_PATH}')

	campaignSheetInfo = GetSpreadsheets()

	for campaignName in campaignSheetInfo:
		for csvPath in campaignSheetInfo[campaignName]:
			WriteSheetToDb(campaignName, csvPath)
