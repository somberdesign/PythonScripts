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
import typing

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
campaignsInDb: typing.Dict[str, int] = {}
encountersInDb: typing.Dict[str, int]

SPREADSHEET_IDS = [
	('Toxic Tribulations', '1DC3uQdeKlIJMbGvJijwTA6AbDN7QjYu5B-ooawjaITc'),
	('Tomb of the Science Wizard', '18W1Kz9ch-Xy729ap6OHkRTHGStJ8pKwiDpLJSRoC6KU')
]
WORKSHEET_POSITIONS = None

class Action:
	def __init__(self):
		self.action: str = ''
		self.hp: int = 0
		self.id: int = 0
		self.primary: str = ''
		self.result: str = ''
		self.round: int = 0
		self.target: str = ''
		self.notes: str = ''
		self.orderInRound: int = 0
	
	def ReadLine(self, line: list, orderInRound: int):
		self.round = line[0]
		self.primary = line[1]
		self.target = line[2]
		self.action = line[3]
		self.result = line[4]
		self.hp = line[5]
		if len(line) > 6: self.notes = line[6]
		self.orderInRound = orderInRound



class Encounter:
	def __init__(self, campaignId: int, encounterName: str):
		self.actions: list = [Action]
		self.campaignId: int = campaignId
		self.encounterName: str = encounterName
		self.id: int


def DbGetCampaigns():
	dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
	interface = db.DatabaseInterface(dbParameters)

	return interface.GetResultSetFromProc('campaigns_get')

def DbGetEncounters(campaignId: int):
	dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
	interface = db.DatabaseInterface(dbParameters)

	result = interface.GetResultSetFromProc('encounters_get_bycampaignid', [campaignId])
	return result


def GetCampaignId(campaignName: str):
	global campaignsInDb

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

def GetEncounterId(campaignId: int, encounterDate: datetime.datetime, encounterName: str):

	IDX_CAMPAIGN_ID = 1
	IDX_ENCOUNTER_ID = 0
	IDX_ENCOUNTER_DATE = 2
	IDX_ENCOUNTER_NAME = 3

	# if encounterName in encountersInDb:
	# 	return encountersInDb[encounterName]

	# one dataset in this result set
	getEncounterResults = DbGetEncounters(campaignId)
	if getEncounterResults is None or len(getEncounterResults) == 0:
		Logger.AddError(f'Can\'t get encounter names when encounterName = {encounterName}')
		return None

#  START HERE

	encounterDataset = getEncounterResults[0]
	for dbEncounter in encounterDataset:
		for campaignEncounter in encountersInDb:
			pass
	
	# encounterDataset = getEncounterResults[0]
	# for e in encounterDataset:


	# if encounterName not in encountersInDb:
	# 	# add to the db
	# 	dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
	# 	interface = db.DatabaseInterface(dbParameters)
	# 	interface.GetResultSetFromProc('encounter_insert', [encounterName])

	# 	encountersInDb[encounterName] = interface[0][0]

	# return encountersInDb[encounterName]
	return 1

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
	IDX_ROUND = 0
	
	LINENUMBER_ENCOUNTER_DATE = 1
	LINENUMBER_COLUMN_HEADERS = 2

	actionDate: datetime.datetime = datetime.datetime.min
	campaignId: int = GetCampaignId(campaignName)
	csvLines: list = ReadCsv.Read(csvPath)
	encounter: Encounter
	orderInRound: int = 0
	roundNumber: int = 0

	def GetEncounterDate(line: list):
		actionDate = datetime.datetime.min
		if len(line[IDX_ACTION_DATE]) > 0:
			tryDate = ToDateTime(line[IDX_ACTION_DATE])
			if tryDate is None:
				Logger.AddError(f'Invalid date: {line[IDX_ACTION_DATE]}. ({csvPath})')
			else:
				actionDate = tryDate

		else:
			Logger.AddWarning(f'Can\'t find date in cell A1. ({campaignName}, {csvPath})')

		return actionDate
	
	lineCounter = 0
	for line in csvLines:
		lineCounter += 1

		# skip blank lines and header row
		if len(''.join(line)) == 0 or lineCounter == LINENUMBER_COLUMN_HEADERS:
			continue

		if lineCounter == LINENUMBER_ENCOUNTER_DATE:
			actionDate = GetEncounterDate(line)
			if actionDate == datetime.datetime.min:
				return False
			continue

		# line is an encounter name
		if len(line[0]) > 0 and len(''.join(line[1:])) == 0:
			encounter = Encounter(campaignId, line[IDX_ENCOUNTER_NAME])
			encounter.id = GetEncounterId(campaignId, actionDate, line[IDX_ENCOUNTER_NAME])
			continue

		# ----- otherwise, line is an action -----

		if len(line[IDX_ROUND]) > 0 and RepresentsInt(line[IDX_ROUND]):
			roundNumber = int(line[IDX_ROUND])
			orderInRound = 0

		if roundNumber == 0:
			Logger.AddWarning(f'Round Number Not Set: Line {lineCounter} ({csvPath})')

		orderInRound += 1

		action = Action()
		action.ReadLine(line, orderInRound)

		if len(line[IDX_ROUND]) > 0 and RepresentsInt(line[IDX_ROUND]): action.round = int(line[IDX_ROUND])
		else: action.round = roundNumber
		
		a = 1
		


		


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
