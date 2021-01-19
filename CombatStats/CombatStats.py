import csv
import glob
import json
import sys
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import os
import shutil
from dateutil.parser import parse as dateParse
import datetime

sys.path.insert(1, r'../DownloadCsv')
import DownloadCsv

sys.path.insert(1, f'../DatabaseInterface')
import DatabaseInterface as db

sys.path.insert(1, r'../ManageCsv')
from ManageCsv import ReadCsv

sys.path.insert(1, r'../Logger')
import Logger

DB_DATABASE_NAME = 'combatstats'
DB_HOST = 'mysql.robiii.dreamhosters.com'
DB_USER = 'marytm'

SECRETS_PATH = '../Secrets.json'
SECRETS_KEY = 'robiii_mysql_password'

dbPassword = ''
campaignsInDb = {str: int}

SPREADSHEET_IDS = [
	('Toxic Tribulations', '1DC3uQdeKlIJMbGvJijwTA6AbDN7QjYu5B-ooawjaITc'),
	('Tomb of the Science Wizard', '18W1Kz9ch-Xy729ap6OHkRTHGStJ8pKwiDpLJSRoC6KU')
]
WORKSHEET_POSITIONS = None

class Actions:
	def __init__(self, round: int, primary: str):
		self.round: int = 0
		self.primary: str = ''
		self.target: str = ''
		self.action: str = ''
		self.result: str = ''
		self.hp: int = 0
		self.notes: str = ''

class Encounter:
	def __init__(self, campaignId: int, encounterName: str):
		self.actions = []
		self.campaignId = campaignId
		self.encounterName = encounterName


def DbGetCampaigns():
	dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
	interface = db.DatabaseInterface(dbParameters)

	return interface.GetResultSetFromProc('campaigns_get')


def GetCampaignId(campaignName: str):

	IDX_CAMPAIGN_ID = 0
	IDX_CAMPAIGN_NAME = 1

	if campaignName in campaignsInDb:
		return campaignsInDb[campaignName]

	# one dataset in this result set
	getCampaignResults = DbGetCampaigns()
	if getCampaignResults is None or len(getCampaignResults) == 0:
		Logger.AddError(f'Can\'t get campaign names when campaignName = {campaignName}')
		return None
	
	campaignDataset = getCampaignResults[0]
	for c in campaignDataset:
		if c[IDX_CAMPAIGN_NAME] not in campaignsInDb:
			campaignsInDb[c[IDX_CAMPAIGN_NAME]] = c[IDX_CAMPAIGN_ID]

	if campaignName not in campaignsInDb:
		# add to the db
		dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
		interface = db.DatabaseInterface(dbParameters)
		interface.GetResultSetFromProc('campaign_insert', [campaignName])

		campaignsInDb[campaignName] = interface[0][0]

	return campaignsInDb[campaignName]


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

def RepresentsInt(inString: str):
	try:
		int(inString)
		return True
	except Exception:
		return False

def ToDateTime(string, fuzzy=False):
	try:
		return dateParse(string, fuzzy=fuzzy)

	except ValueError:
		return None


def WriteSheetToDb(campaignName: str, csvPath: str):
	
	IDX_ACTION_DATE = 0
	IDX_ENCOUNTER_NAME = 0


	LINENUMBER_ENCOUNTER_DATE = 1

	actionDate = datetime.datetime.min
	campaignId = GetCampaignId(campaignName)
	csvLines = ReadCsv.Read(csvPath)
	encounter = None
	
	lineCounter = 0
	for line in csvLines:
		lineCounter += 1

		if lineCounter == LINENUMBER_ENCOUNTER_DATE:
			if len(line[IDX_ACTION_DATE]) > 0:
				tryDate = ToDateTime(line[IDX_ACTION_DATE])
				if tryDate is None:
					Logger.AddError(f'Invalid date: {line[IDX_ACTION_DATE]}. ({csvPath})')
					return
				else:
					actionDate = tryDate
					continue
			else:
				Logger.AddWarning(f'Can\'t find date in cell A1. ({campaignName}, {csvPath})')
				return False

		# line is an action
		if len(line[1]) > 0 and RepresentsInt(line[1]):
			pass

		# line is an encounter name
		if len(line[1]) > 0 and not RepresentsInt(line[1]):
			encounter = Encounter(campaignId, line[IDX_ENCOUNTER_NAME])
			continue


		


if __name__ == "__main__":
	
	if not ReadConfiguration():
		print(f'ERROR: can\'t read configuration file {SECRETS_PATH}')

	campaignSheetInfo = GetSpreadsheets()

	for campaignName in campaignSheetInfo:
		for csvPath in campaignSheetInfo[campaignName]:

			filenameparts = os.path.basename(csvPath).split('_')
			if len(filenameparts) == 1 or not RepresentsInt(filenameparts[0]):
				Logger.AddError(f'Invalid Sheet Name: Format <sheetindex>_<filename>.csv is required. ({csvPath})')
				continue

			# first sheet is the template - skip it
			sheetIndex = int(filenameparts[0])
			if sheetIndex == 0:
				continue

			WriteSheetToDb(campaignName, csvPath)
