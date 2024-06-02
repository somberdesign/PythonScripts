from sys import path
path.insert(1, r'../Logger')

import Logger
from MoveByFilenameConfig import destinationDirectory, firstNamesFile, sourceDirectory

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
				firstNames.append(line.strip().split(",")[0])

	except Exception as ex:
		Logger.AddError(f'Unable to read first names file: {ex}. ({firstNamesFile})')
		return False
	
	return firstNames

if __name__ == '__main__':
	firstNames = ReadFirstNames()

	if not firstNames or len(firstNames) == 0:
		Logger.AddWarning(f"Didn't get any name from first names file")

	for i in firstNames:
		print(i)

