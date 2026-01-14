from sys import path
from unidecode import unidecode
path.insert(1, r'../Logger')

from importlib import import_module
import Logger2 as Logger
from os import listdir, remove
from os.path import isdir, isfile, join
from subprocess import run
from sys import argv
from yaml import safe_load, YAMLError
from string import punctuation

# when True, prints move commands but does not execute them
DEBUG = False
EXTENDED_LOGGING_ENABLED = False
IGNORE_DIRECTORY_PREFIX_CHAR = "_"

def getTargetDirectory(destinationMap, moveDirectoryName:str) -> str:
	
	# return empty string if first character of dir is neither a letter nor number
	if not moveDirectoryName[0].isalpha() and not moveDirectoryName[0].isdigit():
		return str(), 0

	focusDir = moveDirectoryName.split(" ")
	# check for exception to rules
	ruleExceptions = configFile['ruleExceptions']
	if "-" in focusDir:
		artistName = " ".join(map(str, focusDir[0:focusDir.index("-")])).lower()
		if artistName in ruleExceptions:
			return destinationMap[ruleExceptions[artistName]], 1
	
	elif moveDirectoryName.lower() in ruleExceptions:
		return destinationMap[ruleExceptions[moveDirectoryName.lower()]], 2
	
	del ruleExceptions

	# modify focusdir if first name is hyphenated
	# Claude-Michel Schoenberg - The Pirate Queen (Original Broadway Cast Recording)
	if "-" in focusDir[0]:
		newFirstNames = focusDir[0].split("-")
		focusDir.pop(0)
		focusDir = newFirstNames + focusDir

	##### find destination dir #####		

	# title or artist starts with "the"
	if focusDir[0].lower() == "the":
		return destinationMap["the"], 3

	# movie soundtrack
	if any(w.lower() in moveDirectoryName.lower().split() for w in configFile['soundtrackWords']):
		return destinationMap[focusDir[0][0].lower()], 4

	# title only: "A Country Christmas"
	if "-" not in focusDir:
		if moveDirectoryName[0].isnumeric() or moveDirectoryName[0] in punctuation:
			return destinationMap["0"], 5
		else:
			return destinationMap[moveDirectoryName.lower()[0]], 6

	# check to see if artist is a group of people (like "Oscar Peterson Trio")
	for i in range(0, focusDir.index("-")):
		if focusDir[i].lower() in configFile['artistGroupWords']:
			if focusDir[0][0].isnumeric():
				return destinationMap["0"], 11
			else:
				return destinationMap[focusDir[0][0].lower()], 7
	
	# first word of dir is a first name, move file based on last name
	if focusDir[0].lower() in firstNames:

		IGNORED_LAST_NAMES = ["jr", "sr"] # skip titles like, "sr" and "jr"
		lastNamePosition = focusDir.index("-") - 1
		while focusDir[lastNamePosition] in IGNORED_LAST_NAMES and lastNamePosition > 0:
			lastNamePosition -= 1

		return destinationMap[focusDir[lastNamePosition][0].lower()], 8

	# first word is not a name - assume it's the name of a group: "Off the Beat - No Static"
	if moveDirectoryName[0].isnumeric() or moveDirectoryName[0] in punctuation:
		return destinationMap["0"], 9
	else:
		return destinationMap[moveDirectoryName.lower()[0]], 10

def ReadFile(fn):
	fileContents = []
	try:
		with open(fn, 'r') as file:
			fileContents = file.readlines()

	except Exception as ex:
		print(f'Error reading bat file: {ex}. ({fn})')

	return fileContents

def ReadFirstNames():

	# first name file should look like this:
	#
	# Melissa,F,23733
	# Tammy,F,19586
	# Mary,F,19203

	firstNames = []

	try:
		with open(configFile['firstNamesFile'], 'r') as file:
			for line in file:
				firstNames.append(line.strip().split(",")[0].lower())

	except Exception as ex:
		Logger.AddError(f'Unable to read first names file: {ex}. ({configFile['firstNamesFile']})')

	finally:
		file.close()	
	
	return firstNames


# #################################################################################
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

	print(f'configFilename={configFilename}')
	configFile = object()

	with open(configFilename) as stream:
		try:
			configFile = safe_load(stream)
		except YAMLError as ex:
			Logger.AddError(f"Config file is invalid ({configFilename})")
			exit(1)
	
	Logger.SetLogfilePath(configFile['logfilePath'])
	
	firstNames = ReadFirstNames()

	if not firstNames or len(firstNames) == 0:
		if not DEBUG: Logger.AddWarning(f"Didn't get any name from first names file")
		firstNames = []

	if DEBUG: print("DEBUG enabled, will not move directories")

	moveList = []

	# read directories to be moved
	dirsToMove = [f for f in listdir(configFile['sourceDirectory']) if isdir(join(configFile['sourceDirectory'], f))]
	for rawMoveDirectoryName in dirsToMove:

		# ignore dirs that begin with an _
		if rawMoveDirectoryName[0] == IGNORE_DIRECTORY_PREFIX_CHAR and not DEBUG:
			Logger.AddInfo(f'Ignored directory {rawMoveDirectoryName}')
			continue

		moveDirectoryName = unidecode(rawMoveDirectoryName) # replace unicode characters with ascii equivalents
		
		targetDirectory, ruleNumber = getTargetDirectory(configFile['destinationMap'], moveDirectoryName)
		if len(targetDirectory) == 0 and not DEBUG:
			Logger.AddWarning(f'Can''t find target directory for {moveDirectoryName}')
			continue

		fullTargetPath = join(targetDirectory, moveDirectoryName)

		if isdir(fullTargetPath):
			if DEBUG: 
				print(f"moveDirectoryName={moveDirectoryName}, fullTargetPath={fullTargetPath}")
			else:
				Logger.AddInfo(f"Target directory exists: didn't move source directory ({fullTargetPath})")
		else:
			msg = f"Added to move list: {rawMoveDirectoryName} (Rule {ruleNumber}) --> {fullTargetPath}"
			if DEBUG: 
				print(msg)
			else:
				Logger.AddInfo(msg)
				moveList.append([join(configFile['sourceDirectory'], rawMoveDirectoryName), fullTargetPath])


	# write bat file
	# /MOVE delete source files and directory after copy
	# /E makes Robocopy recursively copy subdirectories, including empty ones.
	# /XC excludes existing files with the same timestamp, but different file sizes. Robocopy normally overwrites those.
	# /XN excludes existing files newer than the copy in the destination directory. Robocopy normally overwrites those.
	# /XO excludes existing files older than the copy in the destination directory. Robocopy normally overwrites those.	
	try:
		with open(configFile['batFilename'], 'w') as file:
			for line in moveList:
				file.write(f'robocopy /MOVE /E /XC /XN /XO "{line[0]}" "{line[1]}"\n')
	except Exception as ex:
		msg = f'Unable to write bat file: {ex}. ({configFile['batFilename']})'
		if DEBUG:
			print(msg)
		else:
			Logger.AddError(msg)

	if EXTENDED_LOGGING_ENABLED and not DEBUG:
		if isfile(configFile['batFilename']):
			Logger.AddInfo(f'EXTENDED_LOGGING: bat file {configFile['batFilename']} exists')
		else:
			Logger.AddInfo(f'EXTENDED_LOGGING: bat file {configFile['batFilename']} does NOT exist')


	# execute bat and delete
	
	Logger.AddInfo(f'Executing batch file ({configFile["batFilename"]})')
	if not DEBUG:
		batFile = configFile['batFilename']
		run(batFile, shell=True)	
		Logger.AddInfo("Ended run")

	# else:
	# 	fileContents = ReadFile(configFile['batFilename'])
	# 	for line in fileContents:
	# 		print(f"{line}")

	if DEBUG:
		print(f'DEBUG enabled. Batch file not deleted ({configFile["batFilename"]})')
		input("pause")
	else:
		remove(configFile['batFilename'])

