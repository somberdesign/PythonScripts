from sys import path
path.insert(1, r'../Logger')

import Logger2 as Logger
from MoveByFilenameConfig import batFilename, destinationDirectory, firstNamesFile, logfilePath, sourceDirectory
from os import listdir, remove
from os.path import isdir, join
from subprocess import PIPE, Popen

# from Logger import Logger

def GetTargetDirectory(destinationDirectory:str, moveDirectoryName:str) -> str:
	focusDir = moveDirectoryName.split(" ")

	if focusDir[0].lower() == "the":
		return join(destinationDirectory, "the")

	# title only: "A Country Christmas"
	if "-" not in focusDir:
		if moveDirectoryName[0].isnumeric():
			return join(destinationDirectory, "0")
		else:
			return join(destinationDirectory, moveDirectoryName.lower()[0])

	# first word of dir is a first name, move file based on last name
	if focusDir[0].lower() in firstNames:
		lastNamePosition = focusDir.index("-") - 1
		return join(destinationDirectory, focusDir[lastNamePosition][0].lower())

	# directory start with the name of a group: "Off the Beat - No Static"
	Logger.AddInfo(f'Directory name fell through - assuming name of group. ({moveDirectoryName})')
	if moveDirectoryName[0].isnumeric():
		return join(destinationDirectory, "0")
	else:
		return join(destinationDirectory, moveDirectoryName.lower()[0])

def ReadFirstNames():

	# first name file should look like this:
	#
	# Melissa,F,23733
	# Tammy,F,19586
	# Mary,F,19203

	firstNames = []

	try:
		with open(firstNamesFile, 'r') as file:
			for line in file:
				firstNames.append(line.strip().split(",")[0].lower())

	except Exception as ex:
		Logger.AddError(f'Unable to read first names file: {ex}. ({firstNamesFile})')

	finally:
		file.close()	
	
	return firstNames

if __name__ == '__main__':
	Logger.SetLogfilePath(logfilePath)
	firstNames = ReadFirstNames()

	if not firstNames or len(firstNames) == 0:
		Logger.AddWarning(f"Didn't get any name from first names file")
		firstNames = []

	moveList = []

	# read directories to be moved
	dirsToMove = [f for f in listdir(sourceDirectory) if isdir(join(sourceDirectory, f))]
	for moveDirectoryName in dirsToMove:
		targetDirectory = GetTargetDirectory(destinationDirectory, moveDirectoryName)

		fullTargetDirectory = join(targetDirectory, moveDirectoryName)
		if isdir(fullTargetDirectory):
			Logger.AddInfo(f"Target directory exists: didn't move source directory ({fullTargetDirectory})")
		else:
			Logger.AddInfo(f"Added to move list: {moveDirectoryName} --> {targetDirectory}")
			moveList.append([join(sourceDirectory, moveDirectoryName), fullTargetDirectory])


	# write bat file
	# /MOVE delete source files and directory after copy
	# /E makes Robocopy recursively copy subdirectories, including empty ones.
	# /XC excludes existing files with the same timestamp, but different file sizes. Robocopy normally overwrites those.
	# /XN excludes existing files newer than the copy in the destination directory. Robocopy normally overwrites those.
	# /XO excludes existing files older than the copy in the destination directory. Robocopy normally overwrites those.	
	try:
		with open(batFilename, 'w') as file:
			for line in moveList:
				file.write(f'robocopy "{line[0]}" "{line[1]}" /MOVE /E /XC /XN /XO\n')

	except Exception as ex:
		Logger.AddError(f'Unable to write bat file: {ex}. ({batFilename})')

	finally:
		file.close()

	# execute bat and delete
	p = Popen(batFilename, shell=True, stdout=PIPE)
	stdout, stderr = p.communicate() # p.returncode is 0 if successful
	remove(batFilename)







	
