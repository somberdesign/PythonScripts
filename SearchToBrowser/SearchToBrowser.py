import ctypes
import datetime
import glob
import os
import re
import string
import sys

DIR_TO_SEARCH = r'D:\Users\Bob\PythonScripts\SearchToBrowser'
OUTPUT_FILE = r'D:\Users\Bob\PythonScripts\SearchToBrowser\SearchResults.txt'

def CleanText(line:str) -> str:
	returnVal = re.sub('[^A-Za-z0-9 \n\-]', str(), line)
	return returnVal
	

if __name__ == '__main__':

	# get the number of parameters passed in 
	argc = len(sys.argv)

	# verify the correct number of params 
	if argc < 2:
		ctypes.windll.user32.MessageBoxW(0, 'Missing search term')
		exit(1)

	searchFiles = glob.glob(os.path.join(DIR_TO_SEARCH, '*SmartList.txt'))
	searchTerms = f' {CleanText(sys.argv[1].lower())} '

	if len(searchFiles) == 0:
		ctypes.windll.user32.MessageBoxW(0, f'Can\'t find a SmartList.txt in {DIR_TO_SEARCH}')
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
		ctypes.windll.user32.MessageBoxW(0, f'Stale file list: {stringdate}\nReplace SmartList.txt in {os.path.realpath(__file__)}', 'Stale File List')

	foundLines = []
	for readline in searchLines:
		line = CleanText(readline)
		if searchTerms in line.lower() or searchTerms.rstrip() in line.lower() or searchTerms.lstrip() in line.lower():
			foundLines.append(line)

	with open(OUTPUT_FILE, 'w') as outfile:
		outfile.write(f'Searching: {searchFiles[0]}\n')
		outfile.write(f'Search Terms: {searchTerms.strip()}\n')
		outfile.write(f'Found {len(foundLines)} matches\n\n')
		outfile.writelines(foundLines)
	
	


