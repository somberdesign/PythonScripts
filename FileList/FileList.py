#!/usr/bin/env python

import os
from FileListConfig import *
from datetime import datetime
from json import load
from math import floor
from re import sub
from shutil import copy2

# leave disabled - changes file that is an input to ReadSalesCsv\ModifyMovieList.py
ENABLE_FILENAME_LIMIT = False

ADD_MARKER_TO_ALIASES = False
ALIAS_MARKER = '#'

def FindValidFilename(stem):
	def GetFilename(stem, suffix = ''):
		if suffix == '':
			return datetime.now().strftime('%Y%m%d_') + stem + '.txt'
		else:
			return datetime.now().strftime('%Y%m%d_') + stem + '_' + '{0:0=2d}'.format(suffix) + '.txt'

	if not os.path.isfile(os.path.join(OutputDir, GetFilename(stem))):
		a = 1
		return GetFilename(stem)
	else:
		i = 0
		while os.path.isfile(os.path.join(OutputDir, GetFilename(stem, i))):
			i += 1
		return GetFilename(stem, i)




def GetListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 

    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        
        fullPath = os.path.join(dirName, entry) # Create full path
        
		# If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + GetListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

def GetSmartFiles(dirName):

	ENTRY_LENGTH = 25

	# # 2023-06-08 - this works but will interfere with ReadSalesCsv\ModifyMovieList.py
	# # because it uses SmartList as an input
	# def reduceToFixedLength(inString):
	# 	BASE_STRING_LEN = 25


	# 	returnVal = inString
	# 	if ENABLE_FILENAME_LIMIT and len(inString) > BASE_STRING_LEN:
	# 		backPad = BASE_STRING_LEN - floor(BASE_STRING_LEN * 0.2)
	# 		frontPad = BASE_STRING_LEN - floor((BASE_STRING_LEN + 6) * 0.3)
	# 		returnVal = f'{inString[0:frontPad]}...{inString[-1 * backPad:]}'

	# 	return returnVal

	def reduceToFixedLength(input_string, fixed_length):
		# Check if input_string is already shorter than fixed_length
		if len(input_string) <= fixed_length:
			return input_string
		
		# Calculate number of characters to remove from the middle
		chars_to_remove = len(input_string) - fixed_length
		chars_to_remove_left = chars_to_remove // 2
		chars_to_remove_right = chars_to_remove - chars_to_remove_left
		
		# Remove characters from the middle
		new_string = input_string[:len(input_string)//2 - chars_to_remove_left] + "~" + input_string[len(input_string)//2 + chars_to_remove_right:]
		
		return new_string

	smartFiles = list() # titles reduced to fixed length
	smartFilesFull = list() # complete titles
	jsonInfo = ''
	jsonDescriptions = {}
	smartFileItemName = ''

	# create a json dictionary, if needed
	fullJsonFilename = os.path.join(dirName, JsonInfoFilename);
	if os.path.isfile(fullJsonFilename):
		jsonInfo = None
		try:
			with open(fullJsonFilename) as f:
				jsonInfo = load(f)
		except ValueError as ex:
			print('Invalid JSON (' + fullJsonFilename + ')')
			return False
		except Exception as ex:
			print ('Unable to open json (' + fullJsonFilename + ')')
			return False

		if jsonInfo is not None:

			# create a list of aliases to use in place of specific items
			if 'aliases' in jsonInfo.keys():
				for item in jsonInfo['aliases']:
					if 'itemName' in item and 'description' in item:
						jsonDescriptions[item['itemName']] = item['description'].replace('\\', '')

			# add items to list
			if 'items' in jsonInfo.keys():
				for item in jsonInfo['items']:
					smartFiles.append(reduceToFixedLength(item, ENTRY_LENGTH))
					smartFilesFull.append(item)


	for item in os.listdir(dirName):

		#skip strings that contain an item in the ignore list
		if (
			any(s in item for s in IgnoreStrings)
			or item[0] == '.'
			):
				continue

		# see if there's a description the json file
		if item in jsonDescriptions:
			if ADD_MARKER_TO_ALIASES:
				smartFiles.append(reduceToFixedLength(jsonDescriptions[item] + ALIAS_MARKER, ENTRY_LENGTH))
				smartFilesFull.append(jsonDescriptions[item] + ALIAS_MARKER)
			else:
				smartFiles.append(reduceToFixedLength(jsonDescriptions[item], ENTRY_LENGTH))
				smartFilesFull.append(jsonDescriptions[item])

		else:
			# directory or file name
			smartFileItemName = item

			# look for description files if item is a directory
			if os.path.isdir(os.path.join(dirName, item)):

				#file_id.diz
				if os.path.isfile(os.path.join(dirName, item, InfoFilename)):
					with open(os.path.join(dirName, item, InfoFilename), 'r') as f:
						smartFileItemName = f.readline().rstrip()

			else:
				smartFileItemName = os.path.splitext(smartFileItemName)[0]

			smartFiles.append(reduceToFixedLength(smartFileItemName.replace('_', ' '), ENTRY_LENGTH))
			smartFilesFull.append(smartFileItemName.replace('_', ' '))


	return smartFiles, smartFilesFull

def MoveOldFiles():
	for file in os.listdir(OutputDir):
		if (
			(AllFilesFilenameStem in file or SmartListFilenameStem in file) 
			and file.endswith('.txt')
			and not os.path.isfile(os.path.join(OldFileDir, file))
			):
			try:
				os.rename(os.path.join(OutputDir, file), os.path.join(OldFileDir, file))
			except WindowsError as ex:
				print ('ERROR: Can\'t move file because it already exists in target (' + os.path.join(OutputDir, file) + ')')
				return
			except Exception as ex:
				print ('ERROR: Error moving file: ' + str(ex) + ' (' + os.path.join(OutputDir, file) + ')')
				return

			print('Moved existing file ' + file + ' to ' + os.path.join(OldFileDir, file))

######################################################################### 
def main():
	
	allFiles = list()
	smartFiles = list() # titles reduced to fixed length
	smartFilesFull = list() # complete titles
	
	sortedDirectoryNames = sorted(DirNames, key=lambda set: set.lower())
	print(sortedDirectoryNames)
	
	# put the files from each configured dir into three files:
	# one for all files 
	# two using .directory title name a skipping select files (one has full file names, the other truncated filenames for printing)
	for dirName in sortedDirectoryNames:
		allFiles = allFiles + GetListOfFiles(dirName)
		newSmartFiles, newSmartFilesFull = GetSmartFiles(dirName)
		if newSmartFiles == False:
			print(f'WARNING: Error reading directory {dirName}')
			continue

		smartFiles = smartFiles + newSmartFiles
		smartFilesFull = smartFilesFull + newSmartFilesFull

	MoveOldFiles()

	filePath = os.path.join(OutputDir, FindValidFilename(AllFilesFilenameStem))
	with open(filePath, 'w') as f:
		for item in allFiles:
			f.write('%s\n' % item)
		f.close()
	print('Wrote output file ' + filePath)

	validSmartListFilename = FindValidFilename(SmartListFilenameStem)
	filePath = os.path.join(OutputDir, validSmartListFilename)
	filePathFull = os.path.join(OutputDir, os.path.splitext(validSmartListFilename)[0] + '_full' + os.path.splitext(validSmartListFilename)[1])
	

	rePattern=r'[^A-Za-z0-9 ]+' # sort on alphanumeric and spaces only
	smartFiles = sorted(smartFiles, key=lambda s: sub(rePattern, '', s).lower())
	smartFilesFull = sorted(smartFilesFull, key=lambda s: sub(rePattern, '', s).lower())
	
	# file with shortened titles
	with open(filePath, 'w') as f:
		f.write(datetime.now().strftime('%Y-%m-%d') + '\n')
		f.write(str(len(smartFiles)) + ' items\n')
		f.write('Missing items are (in parentheses)\n')
		f.write('\n')
		for item in smartFiles:
			f.write('%s\n' % item)
		f.close()
	print('Wrote output file ' + filePath)

	# file with full titles
	with open(filePathFull, 'w') as f:
		f.write(datetime.now().strftime('%Y-%m-%d') + '\n')
		f.write(str(len(smartFilesFull)) + ' items\n')
		f.write('Missing items are (in parentheses)\n')
		f.write('\n')
		for item in smartFilesFull:
			f.write('%s\n' % item)
		f.close()
	print('Wrote output file ' + filePathFull)

	#   b. Copy new *_SmartList_Full.txt to ~\ReadSalesCsv\Input\ as "Movie List.txt"
	# see readme at ~\ReadSalesCsv\_readme.txt
	movieListDir = r'..\ReadSalesCsv\Input'
	movieListFilename = 'Movie List.txt'
	movieListFullPath = os.path.join(movieListDir, movieListFilename);
	if os.path.isfile(movieListFullPath): os.remove(movieListFullPath)
	copy2(filePathFull, movieListFullPath)


if __name__ == '__main__':
    main()