from sys import path
path.insert(1, r'../Logger')

import Logger
from MoveByFilenameConfig import batFilename, destinationDirectory, firstNamesFile, sourceDirectory
from os import listdir
from os.path import isdir, join

# from Logger import Logger

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
	firstNames = ReadFirstNames()

	if not firstNames or len(firstNames) == 0:
		Logger.AddWarning(f"Didn't get any name from first names file")
		firstNames = []

	moveList = []

	# read directories to be moved
	dirsToMove = [f for f in listdir(sourceDirectory) if isdir(join(sourceDirectory, f))]
	for d in dirsToMove:
		focusDir = d.split(" ")

		# dir starts with "the"
		if focusDir[0].lower() == "the":
			moveList.append([join(sourceDirectory, d), join(destinationDirectory, "the", d)])
			continue

		# title only: "A Country Christmas"
		if "-" not in focusDir:
			if d[0].isnumeric():
				moveList.append([join(sourceDirectory, d), join(destinationDirectory, "0")])
			else:
				moveList.append([join(sourceDirectory, d), join(destinationDirectory, d.lower()[0])])
			continue

		# first word of dir is a first name, move file based on last name
		if focusDir[0].lower() in firstNames:
			lastNamePosition = focusDir.index("-") - 1
			moveList.append([join(sourceDirectory, d), join(destinationDirectory, focusDir[lastNamePosition][0].lower())])
			continue

		# directory start with the name of a group: "Off the Beat - No Static"
		Logger.AddInfo(f'Directory name fell through - assuming name of group. ({d})')
		if d[0].isnumeric():
			moveList.append([join(sourceDirectory, d), join(destinationDirectory, "0")])
		else:
			moveList.append([join(sourceDirectory, d), join(destinationDirectory, d.lower()[0])])
		continue


	# write bat file
	try:
		with open(batFilename, 'w') as file:
			for line in moveList:
				file.write(f'robocopy "{line[0]}" "{line[1]}" /MOV\n')

	except Exception as ex:
		Logger.AddError(f'Unable to write bat file: {ex}. ({batFilename})')

	finally:
		file.close()


		





	
