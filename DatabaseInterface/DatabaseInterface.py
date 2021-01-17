import json
import os
import sys
import mysql.connector

dbDatabaseName = ''
dbHost = ''
dbPassword = ''
dbUser = ''

class DbParameters:
	global dbDatabaseName
	global dbHost
	global dbPassword
	global dbUser
	
	def __init__(self, host: str, database: str, user: str, password: str):
		dbDatabaseName = database
		dbHost = host
		dbPassword = password
		dbUser = user


def ExecuteProc(procName: str, parameters: list = None):

	if not ReadConfiguration():
		print(f'ERROR: Unable to read configuration file. Executing proc {procName}.')
		return None

	connection = None
	try:
		connection = GetDbConnection()
		if connection is None:
			print('ERROR: No database connection. Exiting.')
			return False

		cursor = connection.cursor()
		
		if parameters is None:
			cursor.callproc(procName)
		else:
			cursor.callproc(procName, parameters)

	except Exception as ex:
		print(f'ERROR: Error executing procedure. {ex}')
		return False

	finally:
		if connection is not None and connection.is_connected():
			connection.close()

	return True

def GetDbConnection():
	
	connection = None
	try:
		connection = mysql.connector.connect(user=dbUser, password=dbPassword, host=dbHost, database=dbDatabaseName)
	except Exception as ex:
		print(f'ERROR: Unable to connect to db. {ex}')
		return None

	return connection

def GetResultSetFromProc(procName: str, parameters: list = None):
	returnVal = None

	if not ReadConfiguration():
		print(f'ERROR: Unable to read configuration file. Executing proc {procName}.')
		return None

	connection = None
	try:
		connection = GetDbConnection()
		if connection is None:
			print('No database connection. Exiting.')
			return None

		cursor = connection.cursor()
		
		if parameters is None:
			cursor.callproc(procName)
		else:
			cursor.callproc(procName, parameters)

		returnVal = []
		for result in cursor.stored_results():
			returnVal.append(result.fetchall())
	
	except Exception as ex:
		print(f'ERROR: Error executing procedure. {ex}')

	finally:
		if connection is not None and connection.is_connected():
			connection.close()

	return returnVal


	global dbPassword

	REQUIRED_FIELDS = ('robiii_mysql_password')
	
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


if __name__ == '__main__':

	ExecuteProc('encounter_insert', [1, 'Will and Grace'])

	# if not ReadConfiguration():
	# 	print('ERROR: Unable to read configuration file')
	# 	exit(1)

	

	# connection = GetDbConnection()
	# if connection is None:
	# 	print('No database connection. Exiting.')
	# 	exit(1)

	# cursor = connection.cursor()

	# cursor.execute('select * from Campaigns')
	# campaigns = cursor.fetchall();
	# for c in campaigns:
	# 	print(c)

	# cursor.callproc('campaign_insert', ['health alert'])
	# cursor.execute('select * from Campaigns')
	# a = 1

	# result = cursor.callproc('campaigns_get')
	# for result in cursor.stored_results():
	# 	print(result.fetchall())

	# connection.close()

	


