

from sys import path
from unidecode import unidecode
path.insert(1, r'../Logger')

from importlib import import_module
import Logger2 as Logger
from os import listdir, remove
from os.path import isdir, isfile, join
from subprocess import PIPE, Popen
from sys import argv
from yaml import safe_load, YAMLError
from string import punctuation






if __name__ == '__main__':


	Logger.SetLogfilePath(".\\DefaultLogFile.log")
	configFilename = str()

	if len(argv) < 2:
		Logger.AddError('Missing configuration filename. USAGE: py MoveByFilename.py [-dry] <configFileName>')
		exit(1)
	
	for i in range(len(argv)):
		if argv[i][0] == "-":
			match argv[i]:
				case "-dry":
					DEBUG = True
				case _:
					Logger.AddWarning(f"Unknown switch ({argv[i]})")

		elif isfile(f"{argv[i]}"):
			configFilename = argv[i]

	if not len(configFilename):
		Logger.AddError(f"Unable to find config file. Exiting. ({configFilename}.py)")
		exit(1)


	with open(configFilename) as stream:
		try:
			configFile = safe_load(stream)
		except YAMLError as ex:
			Logger.AddError(f"Config file is invalid ({configFilename})")
			exit(1)
	
	Logger.SetLogfilePath(configFile['logfilePath'])


