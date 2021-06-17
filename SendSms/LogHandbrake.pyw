import json
import os
import sys
import datetime

LOGFILE_PATH = 'HandbrakeComplete.log'

def PrintUsage():
	print('USAGE: \npy HandbrakeComplete.pyw "messsage text"')

def RepresentsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def WriteLogEntry(message: str):
	now = datetime.datetime.now()  

	with open(LOGFILE_PATH, 'a') as log:
		log.write(f'{now:%Y-%m-%d %H:%M} - {message}\n')
		log.close()



if __name__ == "__main__":

	if len(sys.argv) != 2:
		PrintUsage()
		exit(1)

	WriteLogEntry(f'{sys.argv[1]}')


