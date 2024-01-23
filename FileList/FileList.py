import os
from FileListConfig import *
import datetime
import json
from math import floor

# leave disabled - changes file that is an input to ReadSalesCsv\ModifyMovieList.py
ENABLE_FILENAME_LIMIT = False

ADD_MARKER_TO_ALIASES = False
ALIAS_MARKER = '#'

def FindValidFilename(stem):
	def GetFilename(stem, suffix = ''):
		if suffix == '':
			return datetime.datetime.now().strftime('%Y%m%d_') + stem + '.txt'
		else:
			return datetime.datetime.now().strftime('%Y%m%d_') + stem + '_' + '{0:0=2d}'.format(suffix) + '.txt'

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

	# 2023-06-08 - this works but will interfere with ReadSalesCsv\ModifyMovieList.py
	# because it uses SmartList as an input
	def GetElipsizedString(inString):
		BASE_STRING_LEN = 25


		returnVal = inString
		if ENABLE_FILENAME_LIMIT and len(inString) > BASE_STRING_LEN:
			backPad = BASE_STRING_LEN - floor(BASE_STRING_LEN * 0.2)
			frontPad = BASE_STRING_LEN - floor((BASE_STRING_LEN + 6) * 0.3)
			returnVal = f'{inString[0:frontPad]}...{inString[-1 * backPad:]}'

		return returnVal

	smartFiles = list()
	jsonInfo = ''
	jsonDescriptions = {}
	smartFileItemName = ''

	# create a json dictionary, if needed
	fullJsonFilename = os.path.join(dirName, JsonInfoFilename);
	if os.path.isfile(fullJsonFilename):
		jsonInfo = None
		try:
			with open(fullJsonFilename) as f:
				jsonInfo = json.load(f)
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
					smartFiles.append(GetElipsizedString(item))


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
				smartFiles.append(GetElipsizedString(jsonDescriptions[item] + ALIAS_MARKER))
			else:
				smartFiles.append(GetElipsizedString(jsonDescriptions[item]))

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

			smartFiles.append(GetElipsizedString(smartFileItemName.replace('_', ' ')))


	return smartFiles

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
	smartFiles = list()
	
	sortedDirectoryNames = sorted(DirNames, key=lambda set: set.lower())
	print(sortedDirectoryNames)
	
	# put the files from each configured dir into two files:
	# one for all files and one using .directory title name a skipping select files
	for dirName in sortedDirectoryNames:
		allFiles = allFiles + GetListOfFiles(dirName)
		newSmartFiles = GetSmartFiles(dirName)
		smartFiles = smartFiles + newSmartFiles

	MoveOldFiles()

	filePath = os.path.join(OutputDir, FindValidFilename(AllFilesFilenameStem))
	with open(filePath, 'w') as f:
		for item in allFiles:
			f.write('%s\n' % item)
		f.close()
	print('Wrote output file ' + filePath)

	
	filePath = os.path.join(OutputDir, FindValidFilename(SmartListFilenameStem))
	smartFiles = sorted(smartFiles, key=lambda s: s.lower())
	with open(filePath, 'w') as f:
		f.write(datetime.datetime.now().strftime('%Y-%m-%d') + '\n')
		f.write(str(len(smartFiles)) + ' items\n\n')
		for item in smartFiles:
			f.write('%s\n' % item)
		f.close()
	print('Wrote output file ' + filePath)


if __name__ == '__main__':
    main()