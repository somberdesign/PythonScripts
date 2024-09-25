from sys import path
path.insert(1, r'../Logger')

from importlib import import_module
import Logger2 as Logger
from os import listdir, remove
from os.path import isdir, isfile, join
from subprocess import PIPE, Popen
from sys import argv

# when True, prints move commands but does not execute them
DEBUG = False

def getTargetDirectory(destinationMap, moveDirectoryName:str) -> str:
	
	ruleExceptions = configFile.ruleExceptions
	focusDir = moveDirectoryName.split(" ")

	# check for exception to rule
	if "-" in focusDir and " ".join(map(str, focusDir[0:focusDir.index("-")])).lower() in ruleExceptions:
		return ruleExceptions[" ".join(map(str, focusDir[0:focusDir.index("-")])).lower()]
	elif moveDirectoryName.lower() in ruleExceptions:
		return ruleExceptions[moveDirectoryName.lower()]

	# title or artist starts with the
	if focusDir[0].lower() == "the":
		return destinationMap["the"]

	# title only: "A Country Christmas"
	if "-" not in focusDir:
		if moveDirectoryName[0].isnumeric():
			return destinationMap["0"]
		else:
			return destinationMap[moveDirectoryName.lower()[0]]

	# check to see if artist is a group of people (like "Oscar Peterson Trio")
	for i in range(0, focusDir.index("-")):
		if focusDir[i].lower() in configFile.artistGroupWords:
			return destinationMap[focusDir[0][0].lower()]
	
	# first word of dir is a first name, move file based on last name
	if focusDir[0].lower() in firstNames:

		IGNORED_LAST_NAMES = ["jr", "sr"] # skip titles like, "sr" and "jr"
		lastNamePosition = focusDir.index("-") - 1
		while focusDir[lastNamePosition] in IGNORED_LAST_NAMES and lastNamePosition > 0:
			lastNamePosition -= 1

		return destinationMap[focusDir[lastNamePosition][0].lower()]

	# first word is not a name - assume it's the name of a group: "Off the Beat - No Static"
	if moveDirectoryName[0].isnumeric():
		return destinationMap["0"]
	else:
		return destinationMap[moveDirectoryName.lower()[0]]

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
		with open(configFile.firstNamesFile, 'r') as file:
			for line in file:
				firstNames.append(line.strip().split(",")[0].lower())

	except Exception as ex:
		Logger.AddError(f'Unable to read first names file: {ex}. ({firstNamesFile})')

	finally:
		file.close()	
	
	return firstNames


# #################################################################################
if __name__ == '__main__':
	
	if DEBUG: print("DEBUG enabled, will not move directories")

	Logger.SetLogfilePath(".\\DefaultLogFile.log")

	if len(argv) < 2:
		Logger.AddError('Missing configuration filename. USAGE: py MoveByFilename.py <configFileName>')
		exit(1)
	
	configFilename = argv[1]
	if not isfile(f"{configFilename}.py"):
		Logger.AddError(f"Unable to find config file. Exiting. ({configFilename}.py)")
		exit(1)

	configFile = import_module(configFilename, package=None)
	
	Logger.SetLogfilePath(configFile.logfilePath)
	
	firstNames = ReadFirstNames()

	if not firstNames or len(firstNames) == 0:
		Logger.AddWarning(f"Didn't get any name from first names file")
		firstNames = []

	moveList = []

	# read directories to be moved
	dirsToMove = [f for f in listdir(configFile.sourceDirectory) if isdir(join(configFile.sourceDirectory, f))]
	for moveDirectoryName in dirsToMove:
		targetDirectory = getTargetDirectory(configFile.destinationMap, moveDirectoryName)
		fullTargetPath = join(targetDirectory, moveDirectoryName)

		if isdir(fullTargetPath):
			if DEBUG: print(f"moveDirectoryName={moveDirectoryName}, fullTargetPath={fullTargetPath}")
			Logger.AddInfo(f"Target directory exists: didn't move source directory ({fullTargetPath})")
		else:
			Logger.AddInfo(f"Added to move list: {moveDirectoryName} --> {fullTargetPath}")
			moveList.append([join(configFile.sourceDirectory, moveDirectoryName), fullTargetPath])


	# write bat file
	# /MOVE delete source files and directory after copy
	# /E makes Robocopy recursively copy subdirectories, including empty ones.
	# /XC excludes existing files with the same timestamp, but different file sizes. Robocopy normally overwrites those.
	# /XN excludes existing files newer than the copy in the destination directory. Robocopy normally overwrites those.
	# /XO excludes existing files older than the copy in the destination directory. Robocopy normally overwrites those.	
	try:
		with open(configFile.batFilename, 'w') as file:
			for line in moveList:
				file.write(f'robocopy /MOVE /E /XC /XN /XO "{line[0]}" "{line[1]}"\n')

	except Exception as ex:
		Logger.AddError(f'Unable to write bat file: {ex}. ({configFile.batFilename})')

	# execute bat and delete
	
	if not DEBUG:
		p = Popen(configFile.batFilename, shell=True, stdout=PIPE, stderr=PIPE)
		stdout, stderr = p.communicate() # p.returncode is 0 if successful
		if p.returncode == 0:
			Logger.AddInfo("Ended run")
		else:
			Logger.AddInfo(f"Bat returned {p.returncode}.")
			fileContents = ReadFile(configFile.batFilename)
			for line in fileContents:
				print(f"{line}")
	else:
		fileContents = ReadFile(configFile.batFilename)
		for line in fileContents:
			print(f"{line}")

	remove(configFile.batFilename)







	
