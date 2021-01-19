import sys
import os
import datetime

LOGFILE_PATH = r'CombatStats.log'

def AddError(message: str, displayToConsole:bool=True):
	__WriteEntry__('e', message, displayToConsole)

def AddInfo(message: str, displayToConsole:bool=True):
	__WriteEntry__('i', message, displayToConsole)

def AddWarning(message: str, displayToConsole:bool=True):
	__WriteEntry__('w', message, displayToConsole)


def __WriteEntry__(messageType: str, message: str, displayToConsole: bool):

	now = datetime.datetime.now()

	prefix = 'UNKNOWN'
	if messageType == 'e': prefix = 'ERROR  '
	elif messageType == 'i': prefix = 'INFO   '
	elif messageType == 'w': prefix = 'WARNING'

	if displayToConsole: print(f'{prefix} - {message}\n')

	log = None
	try:
		log = open(LOGFILE_PATH, 'a')

		log.write(f'{now:%Y-%m-%d %H:%M} - {prefix} - {message}\n')

	except:
		print(f'ERROR - unable to write log file {LOGFILE_PATH}\n')

	finally:
		if log is not None and not log.closed:
			log.close()
