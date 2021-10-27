import ctypes
import datetime
import glob
import sys
import os
import string

DIR_TO_SEARCH = r'D:\Users\rgw3\PythonScripts\SearchToBrowser'
OUTPUT_FILE = r'D:\Users\rgw3\PythonScripts\SearchToBrowser\SearchResults.txt'

if __name__ == '__main__':

	# get the number of parameters passed in 
	argc = len(sys.argv)

	# verify the correct number of params 
	if argc < 2:
		print('Missing search term')
		exit(1)

	searchFiles = glob.glob(os.path.join(DIR_TO_SEARCH, '*SmartList.txt'))
	searchTerms = f' {sys.argv[1].lower()} '

	if len(searchFiles) == 0:
		print(f'Can\'t find a SmartList.txt in {DIR_TO_SEARCH}')
		exit(1)

	with open(searchFiles[0], 'r') as f:
		searchLines = f.readlines()

	filedate = None
	stringdate = str()
	try:
		# do some gymnastics. weird chars showing up at beginning of string.
		stringdate = ''.join([s for s in searchLines[0] if s in string.printable]).strip()
		filedate = datetime.datetime.strptime(stringdate, '%Y-%m-%d')
	except Exception as ex:
		ctypes.windll.user32.MessageBoxW(0, f'Invalid date on line 1:\n{stringdate}', 'Document Date Error')
		
	if filedate is not None and (datetime.datetime.now() - filedate).days > 30:
		ctypes.windll.user32.MessageBoxW(0, f'Stale file list: {stringdate}', 'Stale File List')

	foundLines = []
	for line in searchLines:
		if searchTerms in line.lower() or searchTerms.rstrip() in line.lower() or searchTerms.lstrip() in line.lower():
			foundLines.append(line)

	with open(OUTPUT_FILE, 'w') as outfile:
		outfile.write(f'Searchingx: {searchFiles[0]}\n')
		outfile.write(f'Search Terms: {searchTerms.strip()}\n')
		outfile.write(f'Found {len(foundLines)} matches\n\n')
		outfile.writelines(foundLines)
	
	


