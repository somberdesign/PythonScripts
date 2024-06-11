from sys import path
path.insert(1, r'../Logger')

from importlib import import_module
import Logger2 as Logger
from os import listdir, remove
from os.path import isdir, isfile, join
from subprocess import PIPE, Popen
from sys import argv

def GetTargetDirectory(moveDirectoryName:str) -> str:
	from MoveByFilenameConfig import destinationMap
	focusDir = moveDirectoryName.split(" ")

	if focusDir[0].lower() == "the":
		return destinationMap["the"]

	# title only: "A Country Christmas"
	if "-" not in focusDir:
		if moveDirectoryName[0].isnumeric():
			return destinationMap["0"]
		else:
			return destinationMap[moveDirectoryName.lower()[0]]

	# first word of dir is a first name, move file based on last name
	if focusDir[0].lower() in firstNames:
		lastNamePosition = focusDir.index("-") - 1
		return destinationMap[focusDir[lastNamePosition][0].lower()]

	# first word is not a name - assume it's the name of a group: "Off the Beat - No Static"
	if moveDirectoryName[0].isnumeric():
		return destinationMap["0"]
	else:
		return destinationMap[moveDirectoryName.lower()[0]]

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
		targetDirectory = GetTargetDirectory(moveDirectoryName)

		fullTargetDirectory = join(targetDirectory, moveDirectoryName)
		if isdir(fullTargetDirectory):
			Logger.AddInfo(f"Target directory exists: didn't move source directory ({fullTargetDirectory})")
		else:
			Logger.AddInfo(f"Added to move list: {moveDirectoryName} --> {targetDirectory}")
			moveList.append([join(configFile.sourceDirectory, moveDirectoryName), fullTargetDirectory])


	# write bat file
	# /MOVE delete source files and directory after copy
	# /E makes Robocopy recursively copy subdirectories, including empty ones.
	# /XC excludes existing files with the same timestamp, but different file sizes. Robocopy normally overwrites those.
	# /XN excludes existing files newer than the copy in the destination directory. Robocopy normally overwrites those.
	# /XO excludes existing files older than the copy in the destination directory. Robocopy normally overwrites those.	
	try:
		with open(configFile.batFilename, 'w') as file:
			for line in moveList:
				file.write(f'robocopy "{line[0]}" "{line[1]}" /MOVE /E /XC /XN /XO\n')

	except Exception as ex:
		Logger.AddError(f'Unable to write bat file: {ex}. ({configFile.batFilename})')

	finally:
		file.close()

	# execute bat and delete
	p = Popen(configFile.batFilename, shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate() # p.returncode is 0 if successful
	if p.returncode == 0:
		Logger.AddInfo("Ended run")
	else:
		Logger.Addinfo(f"Bat returned {p.returncode}.")
	

	remove(configFile.batFilename)







	
