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

INPUT_SPREADSHEET_PATH = 'InputSheets'

SECRETS_PATH = '../Secrets.json'
SECRETS_KEY = 'robiii_mysql_password'

dbPassword = ''
campaignsInDb: typing.Dict[str, int] = {}
encountersInDb: typing.Dict[str, int]

SPREADSHEET_IDS = [
	('Toxic Tribulations', '1DC3uQdeKlIJMbGvJijwTA6AbDN7QjYu5B-ooawjaITc'),
	('Tomb of the Science Wizard', '18W1Kz9ch-Xy729ap6OHkRTHGStJ8pKwiDpLJSRoC6KU'),
	('Curse of Strahd', '1xKzZOoDwtMADCfCjta-XmLCv79ZBth8ojhJWC8AKK_w')
]
WORKSHEET_POSITIONS = None

class Action:
	IDX_ROUND = 0
	IDX_PRIMARYNAME = 1
	IDX_TARGETNAME = 2
	IDX_ACTION = 3
	IDX_RESULT = 4
	IDX_HITPOINTS = 5
	IDX_NOTES = 6

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
	

	def Dump(self):
		print(f'action={self.action}\nhp={self.hp}\nnotes={self.notes}\norderInRound={self.orderInRound}\nprimary={self.primary}\nresult={self.result}\nround={self.round}\ntarget={self.target}\n')


	def ReadLine(self, line: list, roundNumber:int, orderInRound: int):
		self.action = line[self.IDX_ACTION]
		self.hp = line[self.IDX_HITPOINTS]
		if len(line) > 6: self.notes = line[self.IDX_NOTES]
		self.orderInRound = orderInRound
		self.primary = line[self.IDX_PRIMARYNAME]
		self.result = line[self.IDX_RESULT]
		self.round = roundNumber
		self.target = line[self.IDX_TARGETNAME]


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

def DbGetEncounters(campaignId: int, encounterDate: datetime.datetime=None, encounterName: str=None):
	IDX_ENCOUNTER_DATE: int = 2
	IDX_ENCOUNTER_NAME: str = 3

	dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
	interface = db.DatabaseInterface(dbParameters)
	result = interface.GetResultSetFromProc('encounters_get_bycampaignid', [campaignId])
	
	if encounterDate is None and encounterName is None:
		return result

	if encounterDate is not None and encounterName is None:
		filteredResult = []
		for r in result:
			if r[IDX_ENCOUNTER_DATE].date() == encounterDate.date():
				filteredResult.append(r)
		return filteredResult

	if encounterDate is not None and encounterName is not None:
		filteredResult = []
		for r in result:
			if r[IDX_ENCOUNTER_DATE].date() == encounterDate.date() and r[IDX_ENCOUNTER_NAME].lower() == encounterName.lower():
				filteredResult.append(r)
		return filteredResult

	return None

def DbWriteAction(encounterId: int, action: Action):
	dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
	interface = db.DatabaseInterface(dbParameters)

	parameters = [action.action, encounterId, action.hp, action.notes, action.orderInRound, action.primary, action.result, action.round, action.target]
	result = interface.GetResultSetFromProc('action_insert', parameters)
	

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
	
	# populate campaignsInDb
	campaignDataset = getCampaignResults[0]
	for c in campaignDataset:
		if c[IDX_CAMPAIGN_NAME] not in campaignsInDb:
			campaignsInDb[c[IDX_CAMPAIGN_NAME]] = c[IDX_CAMPAIGN_ID]

	if campaignName not in campaignsInDb:
		
		# add to the db
		dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
		interface = db.DatabaseInterface(dbParameters)
		result = interface.GetResultSetFromProc('campaign_insert', [campaignName])

		campaignsInDb[campaignName] = result[0][0]

	return campaignsInDb[campaignName]

def GetEncounterId(campaignId: int, encounterDate: datetime.datetime, encounterName: str):
	global encountersInDb

	IDX_ENCOUNTER_ID = 0
	IDX_CAMPAIGN_ID = 1
	IDX_ENCOUNTER_DATE = 2
	IDX_ENCOUNTER_NAME = 3
	IDX_ENCOUNTER_ISINACTIVE = 4

	# if encounterName in encountersInDb:
	# 	return encountersInDb[encounterName]

	if encounterName.lower() == '(encountername)':
		return None

	# one dataset in this result set
	getEncounterResults = DbGetEncounters(campaignId)
	if getEncounterResults is None or len(getEncounterResults) == 0:
		Logger.AddError(f'Can\'t get encounter names when encounterName = {encounterName}')
		return None

	encountersInDb = {}
	encounterDataset = getEncounterResults[0] # first dataset returned
	for dbEncounter in encounterDataset:
		encountersInDb[dbEncounter[IDX_ENCOUNTER_NAME]] = dbEncounter[IDX_ENCOUNTER_ID]

	result = None
	if encounterName in encountersInDb:
		return encountersInDb[encounterName]
	else:
		# add to the db
		dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
		interface = db.DatabaseInterface(dbParameters)
		result = interface.GetResultSetFromProc('encounter_insert', [campaignId, encounterName, encounterDate.strftime('%Y-%m-%d')])

	if type(result[0][0]) is int:
		return result[0][0]
	elif type(result[0][0][0]) is int:
		return result[0][0][0]
	else:
		Logger.AddError(f'Unable to find an int for EncounterId when encounter = {encounterName}')
		return None

	return result[0][0][0]

def GetSpreadsheets():
	
	spreadsheetPaths = {}

	# delete old CSVs
	print(f'Deleting CSV directory: {INPUT_SPREADSHEET_PATH}')
	try:
		shutil.rmtree(INPUT_SPREADSHEET_PATH)
	except Exception as ex:
		print(f'Unable to delete directory {INPUT_SPREADSHEET_PATH}. Exiting. {ex}')
		return


	for spreadsheet_id in SPREADSHEET_IDS:

		print(f'\nReading {spreadsheet_id[0]}')
		
		params = DownloadCsv.DownloadGoogleCsv.NewInstanceParameters(spreadsheet_id, WORKSHEET_POSITIONS)
		params.FirstDataLine = 4

		downloadGoogleCsv = DownloadCsv.DownloadGoogleCsv(params)
		csvs = downloadGoogleCsv.DownloadCsvs(INPUT_SPREADSHEET_PATH)

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
	IDX_PRIMARY_NAME = 1
	
	LINENUMBER_ENCOUNTER_DATE = 1
	LINENUMBER_COLUMN_HEADERS = 2

	actionDate: datetime.datetime = datetime.datetime.min
	
	cid = GetCampaignId(campaignName)
	if cid is None:
		Logger.AddError(f'Can\'t find Campaign ID when campaignName is {campaignName}. Skipping sheet.')
		return False

	campaignId: int = cid

	csvLines: list = ReadCsv.Read(csvPath)
	encounter: Encounter = None
	orderInRound: int = 0
	roundNumber: int = 0

	lineCounter = 0
	Logger.AddInfo(f'Reading {csvPath}', prependNewline=True)
	for line in csvLines:

		if line is None:
			print('WARNING: line is none')

		lineCounter += 1

		# skip blank lines and header row
		if line is None or len(''.join(line)) == 0 or lineCounter == LINENUMBER_COLUMN_HEADERS:
			continue

		# check for date, round number or encounter name
		if len(line[0]) > 0:
			trydate = ToDateTime(line[IDX_ACTION_DATE])

			# line contains round number
			if RepresentsInt(line[IDX_ROUND]):
				roundNumber = int(line[IDX_ROUND])
				orderInRound = 0
				print(f'Round: {roundNumber}')

			# change action date
			elif not RepresentsInt(line[IDX_ACTION_DATE]) and trydate is not None:
				actionDate = trydate
				print(f'Action Date: {actionDate}')

			# line contains encounter name
			else:
				encounter = Encounter(campaignId, line[IDX_ENCOUNTER_NAME])
				encounter.id = GetEncounterId(campaignId, actionDate, line[IDX_ENCOUNTER_NAME])
				print(f'Encounter Name: {line[IDX_ENCOUNTER_NAME]}')

		# ----- otherwise, line is an action -----
		if encounter is None:
			print('Haven\'t found encounter name yet')
			continue

		if encounter.id is None:
			Logger.AddWarning(f'Encounter ID is undefined. (Line {lineCounter}, {csvPath}')
			continue

		# skip line if it doesn't contain a primary name
		if len(line[IDX_PRIMARY_NAME]) == 0:
			continue


		if roundNumber == 0:
			Logger.AddWarning(f'Round Number Not Set: Line {lineCounter} ({csvPath})')

		orderInRound += 1

		action = Action()
		action.round = roundNumber
		action.ReadLine(line, roundNumber, orderInRound)
		DbWriteAction(encounter.id, action)

		a = 1
		
		


if __name__ == "__main__":
	
	if not ReadConfiguration():
		print(f'ERROR: can\'t read configuration file {SECRETS_PATH}')

	for root, dirs, files in os.walk(r'..\DownloadCsv\csvs'):
		for filename in files:
			csvPath = os.path.join(root, filename)
			print(f'{csvPath}')
			
			
			filenameparts = filename.split('_') # filename has three parts: <sheetIndex(int)>_<title>_<sheetname>.csv
			if len(filenameparts) != 3 or not RepresentsInt(filenameparts[0]):
				Logger.AddError(f'Invalid Sheet Name: Format <sheetindex>_<spreadsheetName>_<worksheetName>.csv is required. ({csvPath})')
				continue

			# first sheet is the template - skip it
			sheetIndex = int(filenameparts[0])
			if sheetIndex == 0:
				continue

			WriteSheetToDb(filenameparts[1], csvPath)
