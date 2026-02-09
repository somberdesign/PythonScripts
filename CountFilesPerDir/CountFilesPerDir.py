from datetime import datetime as dt
from datetime import timedelta
from math import floor
import os
import sys
# from yaml import safe_load, YAMLError
from subprocess import Popen, run
from pyperclip import copy as pyperclipCopy
from random import choice, seed

# Counts the number of files with a specific filetype under the target dir

# TARGET_FILETYPE = 'url'
# SPACES = ' ' * 15
BLOCKCHAR = '-'
BLOCKDAYS = [2, 6] # list of days-of-the-week (to place a fixed char instead of the file count. 0=Mon, 1=Tue...
BLOCKDATES = ['2026-03-16','2026-03-17','2026-03-18','2026-03-19','2026-03-20','2026-03-21','2026-03-22'] # list of specific dates (yyyy-mm-dd) to block
DAYLIMIT = 55 # number of days into the future to process
FILE_EXPLORER_LOCATION = r"C:\Portable\FreeCommander\FreeCommander.exe"


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
	lowItemCount = 1000
	lowSeriesCount = 1000
	lowItemDirs = []
	lowSeriesDirs = []
	lowSeriesDirs = []

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

			# don't look at blocked days when figuring out lowest item counts
			directoryDateString = dir[:-4] # dir looks like this: 2025-08-21-Thu
			directoryDate = dt.strptime(directoryDateString, '%Y-%m-%d')

			if not IsBlockedDate(directoryDateString):
				if len(items) == lowItemCount:
					lowItemDirs.append(testDir)
				
				elif len(items) < lowItemCount:
					lowItemDirs.clear()
					lowItemDirs.append(testDir)
					lowItemCount = len(items)

				if len(seriesItems) == lowSeriesCount:
					lowSeriesDirs.append(testDir)
				
				elif len(seriesItems) < lowSeriesCount:
					lowSeriesDirs.clear()
					lowSeriesDirs.append(testDir)
					lowSeriesCount = len(seriesItems)


			results[testDir] = len(items), len(seriesItems)
	
	seed(dt.now().microsecond) # improve randomness?
	return { 
		'results': results, 
		'lowestItemDate': choice(lowItemDirs), 
		'lowestSeriesDate': choice(lowSeriesDirs) 
	}

def CountFiles(targetDir:str):
	results = []
	# loop over date dirs
	for dir in [d for d in os.listdir(targetDir) if os.path.isdir(os.path.join(targetDir, d))]:
		filecount = len([f for f in os.listdir(os.path.join(targetDir, dir))])
		results.append((filecount, f'{filecount:03}\t{dir}'))

	results.sort(key=lambda tup:tup[0]) # sort by number of files in dir
	for item in results:
		print(item[1])

def IsBlockedDate(dirstring):
	parts = dirstring.split('-')
	
	if (
		len(parts) != 3
		or not RepresentsInt(parts[0])
		or not RepresentsInt(parts[1])
		or not RepresentsInt(parts[2])
		):
		return False
		
	dateString = f'{parts[0]}-{parts[1]}-{parts[2]}'
	dayOfWeek = dt.strptime(dateString, '%Y-%m-%d').weekday()
	return dateString in BLOCKDATES or dayOfWeek in BLOCKDAYS

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
		allResults = CountDirectories(targetDir)
		directoryData = allResults['results']
		
		if len(directoryData) > 0:
			dateSpaces = ' ' * (floor(len(list(directoryData.items())[0][0]) / 2) - 2)
			print(f'{dateSpaces}DATE               SINGLES  SERIES  ')
			for item in directoryData.items():
				dayString = item[0][-14:-4]
				if IsBlockedDate(dayString):
					singleValue = BLOCKCHAR
					seriesValue = BLOCKCHAR
				else:
					singleValue = item[1][0] if item[1][0] > 0 else " "
					seriesValue = item[1][1] if item[1][1] > 0 else " "
			
				# print(f'{item[0]}    {item[1][0] if item[1][0] > 0 else " "}       {item[1][1] if item[1][1] > 0 else " "} ')
				print(f'{item[0]}    {singleValue}       {seriesValue}')

			lowestItemDate = allResults['lowestItemDate']
			print(f'\nIndividual Pick: {lowestItemDate} (clipboard)')
			print(f'Series Pick    : {allResults['lowestSeriesDate']}')

			pyperclipCopy(lowestItemDate)
			completedProcess = run([FILE_EXPLORER_LOCATION, lowestItemDate])
	
	# input('\nPress ENTER to exit...')