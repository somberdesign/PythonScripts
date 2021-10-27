import datetime
import ftplib
import json
import os
import sys

sys.path.insert(1, f'../DatabaseInterface')
import DatabaseInterface as db

sys.path.insert(1, r'../Logger')
import Logger


DB_DATABASE_NAME = 'combatstats'
DB_HOST = 'mysql.robiii.dreamhosters.com'
DB_USER = 'marytm'
dbPassword = None

FTP_SECRETS_KEYS = ['ftp_address', 'ftp_login', 'ftp_password', 'ftp_upload_directory', 'http_upload_directory']
FTP_SECRETS_PATH = '../CreateStatsHtml_Secrets.json'
ftpInfo = {}

HTML_TEMPLATE_PATH = 'Templates/PlayerStatsHtmlTemplate.html'
OUTPUT_DIR = 'HtmlOutput'

SECRETS_PATH = '../Secrets.json'
SECRETS_KEY = 'robiii_mysql_password'

def CreateReport_UNUSED(datasets):

	def GetTotals(dataset):
		IDX_ENCOUNTER_DATE = 0
		IDX_ENCOUNTER_NAME = 1
		IDX_PRIMARY_NAME = 2
		IDX_TOTAL= 3

		currentEncounterName = ''
		encounters = {}
		
		insertHtml = '''
		<div class="statBlock" id="divDamageDealt">
			<table class="statTable">
		'''

		rowCounter = 0
		for row in dataset:
			rowCounter += 1
			
			# start a new encounter
			if currentEncounterName != row[IDX_ENCOUNTER_NAME]:
				insertHtml += f'<tr class="trHeader"><td class="tdHeader" colspan="2">{row[IDX_ENCOUNTER_DATE]} &mdash; {row[IDX_ENCOUNTER_NAME]}'
				currentEncounterName = row[IDX_ENCOUNTER_NAME]
				actions = {}

			evenOdd = 'even' if rowCounter % 2 == 0 else 'odd'
			insertHtml += f'''
			<tr class="data-row-{evenOdd}">
				<td class="data-cell-{evenOdd}">{row[IDX_PRIMARY_NAME]}</td>
				<td class="data-cell-{evenOdd}">{row[IDX_TOTAL]}</td>
			</tr>
			'''
			
				
		insertHtml += '</table>'
		insertHtml += '</div>'

		return insertHtml


	IDX_DS_CAMPAIGNNAME = 0
	IDX_DS_DAMAGEDEALT = 1
	IDX_DS_DAMAGETAKEN = 2
	IDX_DS_DAMAGEBYACTION = 3

	if not os.path.isdir(OUTPUT_DIR): os.mkdir(OUTPUT_DIR)

	report = None
	try:
		with open(HTML_TEMPLATE_PATH, 'r') as file:
			report = file.read()
	except Exception as ex:
		Logger.AddError(f'Unable to open html template. {ex} ({HTML_TEMPLATE_PATH})')
		return False

	campaignName = datasets[IDX_DS_CAMPAIGNNAME][0][0]
	report = report.replace('$_CAMPAIGN_NAME', campaignName)
	report = report.replace('$_DAMAGE_INFLICTED', GetTotals(datasets[IDX_DS_DAMAGEDEALT]))
	report = report.replace('$_DAMAGE_TAKEN', GetTotals(datasets[IDX_DS_DAMAGETAKEN]))
	report = report.replace('$_DAMAGE_BYACTION', GetTotals(datasets[IDX_DS_DAMAGEBYACTION]))







	outputPath = os.path.join(OUTPUT_DIR, campaignName + '.html')
	print(f'Writing report to {os.path.abspath(outputPath)}')
	try:
		with open(outputPath, 'w') as file:
			file.write(report)
	except Exception as ex:
		Logger.AddError(f'Unable to write report: {ex}. ({outputPath})')
		return False

	return True

def GetStatsHtml(dataset):

	IDX_ENCOUNTER_DATE: int = 0
	IDX_ENCOUNTER_NAME: int = 1
	IDX_PRIMARY_NAME: int = 2
	IDX_ATTACKS_MADE: int = 3
	IDX_HIT_RATIO: int = 4
	IDX_DAMAGE_INFLICTED: int = 5
	IDX_ATTACKS_DEFENDED: int = 6
	IDX_DEFENSE_RATIO: int = 7
	IDX_DAMAGE_RECEIVED: int = 8
	IDX_HEALING_PROVIDED: int = 9
	IDX_HEALING_RECEIVED: int = 10
	IDX_BUFFS_PROVIDED: int = 11
	IDX_BUFFS_RECEIVED: int = 12
	IDX_CURSES_PROVIDED: int = 13
	IDX_CURSES_RECEIVED: int = 14

	def FormatDecimal(value):
		if value is None:
			return '&nbsp;'
		return f'{value:.2f}'

	if not os.path.isdir(OUTPUT_DIR): os.mkdir(OUTPUT_DIR)

	currentEncounterName = ''
	
	insertHtml = '''
	<div class="statBlock" id="divDamageDealt">
		<table class="statTable">
	'''

	rowCounter = 0
	topEncounterRow = False
	for row in dataset:
		rowCounter += 1
		
		# start a new encounter
		if currentEncounterName != row[IDX_ENCOUNTER_NAME]:
			# if len(currentEncounterName) > 0: insertHtml += '</tr>' # don't terminate row first time though
			topEncounterRow = True
			insertHtml += f'''
				<tr class="trHeader"><td class="td-header" colspan="11">{row[IDX_ENCOUNTER_DATE]} &mdash; {row[IDX_ENCOUNTER_NAME]}</td></tr>
				<tr>
					<td class="td-header-2 data-cell-primary_name">&nbsp;</td>
					<td class="td-header-2 data-cell-attacks_made">Attacks<br />Made</td>
					<td class="td-header-2 data-cell-hit_ratio">Hit<br />Ratio</td>
					<td class="td-header-2 data-cell-damage_inflicted">Damage<br />Dealt</td>
					<td class="td-header-2 data-cell-attacks_defended">Attacks<br />Received</td>
					<td class="td-header-2 data-cell-defense_ratio">Defense<br />Ratio</td>
					<td class="td-header-2 data-cell-damage_received">Damage<br />Received</td>
					<td class="td-header-2 data-cell-healing_provided">Healing<br />Granted</td>
					<td class="td-header-2 data-cell-healing_received">Healing<br />Received</td>
					<td class="td-header-2 data-cell-buffs_provided">Buffs<br />Granted</td>
					<td class="td-header-2 data-cell-buffs_received">Buffs<br />Received</td>
					<td class="td-header-2 data-cell-curses_provided">Curses<br />Dealt</td>
					<td class="td-header-2 data-cell-curses_received">Curses<br />Received</td>
				</tr>
			'''
			currentEncounterName = row[IDX_ENCOUNTER_NAME]

		evenOdd = 'even' if rowCounter % 2 == 0 else 'odd'
		topRowClass = ' group-border-top' if topEncounterRow else ''
		insertHtml += '<tr>'

		# player name
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-primary-name">{row[IDX_PRIMARY_NAME]}</td>'

		# attacks
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-attacks-made group-border-left{topRowClass}">{row[IDX_ATTACKS_MADE]}</td>'
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-hit-ratio{topRowClass}">{FormatDecimal(row[IDX_HIT_RATIO])}</td>'
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-damage-inflicted group-border-right{topRowClass}">{row[IDX_DAMAGE_INFLICTED]}</td>'

		# defense
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-attacks-defended group-border-left{topRowClass}">{row[IDX_ATTACKS_DEFENDED]}</td>'
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-defense-ratio{topRowClass}">{FormatDecimal(row[IDX_DEFENSE_RATIO])}</td>'
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-damage-received group-border-right{topRowClass}">{row[IDX_DAMAGE_RECEIVED]}</td>'

		# healing and buffs
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-healing-provided group-border-left{topRowClass}">{row[IDX_HEALING_PROVIDED]}</td>'
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-healing-received{topRowClass}">{row[IDX_HEALING_RECEIVED]}</td>'
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-healing-provided{topRowClass}">{row[IDX_BUFFS_PROVIDED]}</td>'
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-healing-received{topRowClass}">{row[IDX_BUFFS_RECEIVED]}</td>'
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-healing-provided{topRowClass}">{row[IDX_CURSES_PROVIDED]}</td>'
		insertHtml += f'<td class="data-cell data-cell-{evenOdd} data-cell-healing-received group-border-right{topRowClass}">{row[IDX_CURSES_RECEIVED]}</td>'
		
		insertHtml += '</tr>'
		topEncounterRow = False
			
	insertHtml += '</table>'
	insertHtml += '</div>'

	return insertHtml


def GetStats(campaignId:int):
	dbParameters = db.DatabaseInterface.DbParameters(DB_HOST, DB_DATABASE_NAME, DB_USER, dbPassword)
	interface = db.DatabaseInterface(dbParameters)

	return interface.GetResultSetFromProc('player_stats_byCampaignId', [campaignId])

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

def UploadFile(filepath: str):

	def ReadFtpConfiguration():
		global ftpInfo

		# read file
		data = None
		try:
			with open(FTP_SECRETS_PATH) as json_file:
				data = json.load(json_file)
		except Exception as ex:
			print(f'Exception opening {FTP_SECRETS_PATH}: {ex}')
			return False

		if data is None:
			print(f'Failed to read {FTP_SECRETS_PATH}')
			return False

		# loop over secret file keys
		foundAllKeys = True
		for key in FTP_SECRETS_KEYS:
			if key in data:
				ftpInfo[key] = data[key]
			else:
				print(f'Can\'t find key {key} in config file {FTP_SECRETS_PATH}')
				foundAllKeys = False
		if not foundAllKeys: return False

		return True 
	
	if not ReadFtpConfiguration():
		Logger.AddError('Error reading FTP config file')
		return False

	uploadFilename = os.path.basename(filepath).replace(' ', '_')

	try:
		ftp = ftplib.FTP(ftpInfo['ftp_address'], ftpInfo['ftp_login'], ftpInfo['ftp_password'])
		ftp.encoding = 'utf-8'
		ftp.cwd(ftpInfo['ftp_upload_directory'])
		
		with open(filepath, 'rb') as file:
			ftp.storbinary(f'STOR {uploadFilename}', file)

		print(f'Uploaded file at {ftpInfo["http_upload_directory"]}/{uploadFilename}')
	except Exception as ex:
		print(f'Error uploading file. ({ex})')
		return False

	finally:
		ftp.quit()
	
	return True


if __name__ == "__main__":
	
	if len(sys.argv) < 2 or not RepresentsInt(sys.argv[1]):
		print('USAGE: py CreateStatsHtml.py <CampaignId>')
		exit(1)

	campaignId = int(sys.argv[1])

	if not ReadConfiguration():
		print(f'ERROR: can\'t read configuration file {SECRETS_PATH}')

	datasets = GetStats(campaignId)
	campaignName = datasets[0][0][0]

	reportInfo = f'<div class="div-report-info"><span title="{datetime.datetime.now():%Y%d%m %HH%MM}">Report Date: {datetime.datetime.now():%m/%d/%Y}</span>'
	if len(datasets[0][0][1]) > 0: reportInfo += f'<br /><a href="{datasets[0][0][1]}" target="_new">Source Data</a>'
	reportInfo += '</div>'
	
	report = None
	try:
		with open(HTML_TEMPLATE_PATH, 'r') as file:
			report = file.read()
	except Exception as ex:
		Logger.AddError(f'Unable to open html template. {ex} ({HTML_TEMPLATE_PATH})')
		exit(1)

	statsHtml = GetStatsHtml(datasets[1])
	report = report.replace('$_CAMPAIGN_NAME', campaignName)
	report = report.replace('$_REPORT_INFO', reportInfo)
	report = report.replace('$_PLAYER_STATS', statsHtml)



	outputPath = os.path.join(OUTPUT_DIR, campaignName + '.html')
	print(f'Writing report to {os.path.abspath(outputPath)}')
	try:
		with open(outputPath, 'w') as file:
			file.write(report)
	except Exception as ex:
		Logger.AddError(f'Unable to write report: {ex}. ({outputPath})')
		exit(1)

	UploadFile(outputPath)
		