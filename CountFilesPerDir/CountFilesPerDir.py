from datetime import datetime as dt
from datetime import timedelta
import fuzzywuzzy
import os
import sys

# Counts the number of files with a specific filetype unsder the target dir

TARGET_FILETYPE = 'url'

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

	results = {}
	for dir in [d for d in os.listdir(targetDir) if os.path.isdir(os.path.join(targetDir, d))]:
		
		if GetDirDate(dir) < dt.now() or GetDirDate(dir) > dt.now() + timedelta(days=30):
			continue
		
		items = []
		testDir = os.path.join(targetDir, dir)
		for f in os.listdir(testDir):

			testItem = os.path.join(targetDir, dir, f)
			if not os.path.isdir(testItem):
				continue

			halfstring = f[:int(len(f) / 2)]
			if len(items) == 0:
				items.append(halfstring)
				continue
				
			if halfstring in items:
				continue
				
			items.append(halfstring)
			
		results[testDir] = len(items)

			# if not os.path.isdir(testItem) and os.path.splitext(testItem)[1] == f'.{TARGET_FILETYPE}':
				# print(f)
				# if testDir in results.keys():
					# results[testDir] += 1
				# else:
					# results[testDir] = 1
					
	for item in [v[0] for v in sorted(results.items(), key=lambda kv: (-kv[1], kv[0]))]:
		print(f'{item}  {results[item]}')
		
	input()