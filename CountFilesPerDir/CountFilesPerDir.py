from datetime import datetime as dt
from datetime import timedelta
from math import floor
import os
import sys

# Counts the number of files with a specific filetype under the target dir

TARGET_FILETYPE = 'url'
SPACES = ' ' * 15
DAYLIMIT = 45

# 2023-12-29 - just had the cataract in my right eye removed
# expected dir structure is as follows:
# ~
#  |-- 2024-01
#     |-- 2024-01-01-Mon
#     |-- 2024-01-02-Tue
#  |-- 2024-02
#     |-- 2024-02-01-Thu
#     |-- 2024-02-02-Fri


def CountDirectories(targetDir:str):
	results = {}

	# loop over month dirs
	for monthdir in [d for d in os.listdir(targetDir) if os.path.isdir(os.path.join(targetDir, d))]:

		# loop over date dirs
		for dir in [d for d in os.listdir(os.path.join(targetDir, monthdir)) if os.path.isdir(os.path.join(targetDir, monthdir, d))]:
			
			# limit number of dirs that are processed
			if GetDirDate(dir) < dt.now() or GetDirDate(dir) > dt.now() + timedelta(days=DAYLIMIT):
				continue
			
			items:list = []
			seriesItems:list = []
			testDir = os.path.join(targetDir, monthdir, dir)
			
			# loop over items in date dir
			for f in os.listdir(testDir):

				testItem = os.path.join(testDir, f)
				
				# skip files
				if not os.path.isdir(testItem):
					continue

				# ignore dirs beginning with _
				if f[0] == '_':
					continue

				halfstring = f[:int(len(f) / 2)]
				if len(items) == 0:
					items.append(halfstring)
					continue
					
				# assume it's part of a series if the first half of the string has been seen before
				if halfstring in items:
					if halfstring not in seriesItems: seriesItems.append(halfstring)
					continue
				
				# assume it's an individual title if you get here
				items.append(halfstring)

				if len(items) > 0:
					a = 1
			
			# remove series titles from individual item list
			for i in seriesItems:
				if i in items: items.remove(i)

			results[testDir] = len(items), len(seriesItems)
	
	return results

def CountFiles(targetDir:str):
	results = []
	# loop over date dirs
	for dir in [d for d in os.listdir(targetDir) if os.path.isdir(os.path.join(targetDir, d))]:
		filecount = len([f for f in os.listdir(os.path.join(targetDir, dir))])
		results.append((filecount, f'{filecount:03}\t{dir}'))

	results.sort(key=lambda tup:tup[0]) # sort by number of files in dir
	for item in results:
		print(item[1])

def ProcessCommandLine():
	returnVal = [str(), []]
	validArguments = ['countfiles']

	# get the number of parameters passed in
	argc = len(sys.argv)
	
	# verify corrrect number of params
	if argc < 2:
		print('USAGE: py CountFilesPerDir.py <targetDir>')
		exit(1)

	# verify param is an xml file
	targetDir = sys.argv[1]
	if not os.path.isdir(targetDir):
		print(f'Invalid directory ({targetDir})')
		exit(1)
	returnVal[0] = targetDir

	if argc > 2:
		for i in range(2, argc):
			arg = sys.argv[i]
			if len(arg) < 3 or arg[:2] != '--' or arg[2:].lower() not in validArguments:
				print(f'Invalid argument: {arg}')
				continue
			returnVal[1].append(arg)

	return returnVal


def GetDirDate(dirstring):
	returnVal = dt(1970, 1, 1)
	parts = dirstring.split('-')
	
	if (
		len(parts) != 4
		or not RepresentsInt(parts[0])
		or not RepresentsInt(parts[1])
		or not RepresentsInt(parts[2])
		):
		return returnVal
		
	try:
		returnVal = dt(int(parts[0]), int(parts[1]), int(parts[2]))
	except Exception as ex:
		return returnVal
		
	return returnVal

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False	

if __name__ == '__main__':
	

	arguments = ProcessCommandLine()
	targetDir = arguments[0]

	if '--countfiles' in arguments[1]:
		CountFiles(targetDir)

	else:
		directoryData = CountDirectories(targetDir)
		if len(directoryData) > 0:
			dateSpaces = ' ' * (floor(len(list(directoryData.items())[0][0]) / 2) - 2)
			print(f'{dateSpaces}DATE             SINGLES  SERIES  ')
			# for item in [v[0] for v in sorted(results.items(), key=lambda kv: (-kv[1][0], kv[0]))]:
			for item in directoryData.items():
				print(f'{item[0]}    {item[1][0] if item[1][0] > 0 else " "}       {item[1][1] if item[1][1] > 0 else " "} ')

		
	input()