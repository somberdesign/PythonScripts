import json
import os
import sys
import mysql.connector

class DatabaseInterface:

	dbDatabaseName = ''
	dbHost = ''
	dbPassword = ''
	dbUser = ''

	class DbParameters:
		
		dbDatabaseName = ''
		dbHost = ''
		dbPassword = ''
		dbUser = ''

		def __init__(self, host: str, database: str, user: str, password: str):
			self.dbDatabaseName = database
			self.dbHost = host
			self.dbPassword = password
			self.dbUser = user

	def __init__(self, databaseParameters: DbParameters):
		self.dbDatabaseName = databaseParameters.dbDatabaseName
		self.dbHost = databaseParameters.dbHost
		self.dbPassword = databaseParameters.dbPassword
		self.dbUser = databaseParameters.dbUser

	def ExecuteProc(self, procName: str, parameters: list = None):

		connection = None
		try:
			connection = self.GetDbConnection()
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

	def GetDbConnection(self):
		
		connection = None
		try:
			connection = mysql.connector.connect(user=self.dbUser, password=self.dbPassword, host=self.dbHost, database=self.dbDatabaseName)
		except Exception as ex:
			print(f'ERROR: Unable to connect to db. {ex}')
			return None

		return connection

	def GetResultSetFromProc(self, procName: str, parameters: list = None):
		returnVal = None

		connection = None
		try:
			connection = self.GetDbConnection()
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


	


