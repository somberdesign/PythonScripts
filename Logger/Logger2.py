import sys
from os.path import isdir, split
import datetime

LOGFILE_PATH = r'Logger.log'

def __init__(self, logfilePath: str):
	global LOGFILE_PATH
	SetLogfilePath(logfilePath)
	

def AddError(message: str, displayToConsole:bool=True, prependNewline:bool=False, appendNewline:bool=False):
	__WriteEntry__('e', message, displayToConsole, prependNewline=prependNewline, appendNewline=appendNewline)

def AddInfo(message: str, displayToConsole:bool=True, prependNewline:bool=False, appendNewline:bool=False):
	__WriteEntry__('i', message, displayToConsole, prependNewline=prependNewline, appendNewline=appendNewline)

def AddWarning(message: str, displayToConsole:bool=True, prependNewline:bool=False, appendNewline:bool=False):
	__WriteEntry__('w', message, displayToConsole, prependNewline=prependNewline, appendNewline=appendNewline)

def SetLogfilePath(logfilePath:str):
	splitPath = split(logfilePath)
	if not isdir(splitPath[0]):
		return [False, f'Logger: invalid logfile directory ({splitPath[0]})']
	
	global LOGFILE_PATH 
	LOGFILE_PATH = logfilePath
	return [True, '']


def __WriteEntry__(messageType: str, message: str, displayToConsole: bool, prependNewline:bool=False, appendNewline:bool=False):

	now = datetime.datetime.now()

	prefix = 'UNKNOWN'
	if messageType == 'e': prefix = 'ERROR  '
	elif messageType == 'i': prefix = 'INFO   '
	elif messageType == 'w': prefix = 'WARNING'

	if displayToConsole: 
		if prependNewline: print('\n')
		print(f'{prefix} - {message}')
		if appendNewline: print('\n')

	log = None
	try:
		log = open(LOGFILE_PATH, 'a')

		log.write(f'{now:%Y-%m-%d %H:%M} - {prefix} - {message}\n')

	except:
		print(f'ERROR - unable to write log file {LOGFILE_PATH}\n')

	finally:
		if log is not None and not log.closed:
			log.close()
