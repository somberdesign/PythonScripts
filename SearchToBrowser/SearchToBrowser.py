import ctypes
import datetime
import glob
import os
from pathvalidate import sanitize_filename
import pyperclip
import re
import string
import sys
from time import time
from typing import Tuple
from subprocess import call

DIR_TO_SEARCH = r'E:\Users\Bob\PythonScripts\SearchToBrowser'
OUTPUT_DIRECTORY = r'E:\temp\searchToBrowser'
EVERYTHING_COMMAND_LINE_PATH = r'"C:\Program Files\Everything\es.exe"' # leave empty to disable

def CleanText(line:str) -> str:
	returnVal = re.sub('[^A-Za-z0-9 \n\-\~]', str(), line)
	return returnVal
	
def GetArguments(configValues:dict) -> Tuple:

	# get the number of parameters passed in 
	argc = len(sys.argv)

	# verify the correct number of params 
	# arg[1] = file to search
	# arg[2] = search term
	if argc < 3:
		return False, 'Usage: SearchToBrowser.py <searchfile> <searchterm>'

	searchFile = sys.argv[1]
	if '*' in sys.argv[1]:
		searchFile = str()
		candidates = glob.glob(sys.argv[1])
		if len(candidates) > 0:
			searchFile = candidates[0]


	if not os.path.isfile(searchFile):
		return False, f'{searchFile} is not a file' if len(searchFile) > 0 else f'Unable to find match at {searchFile}'

	configValues['searchfilepath'] = searchFile
	configValues['searchterm'] = sys.argv[2]

	return True, str()


if __name__ == '__main__':

	configValues = {
		'searchfilepath' : str(),
		'searchterm' : str()
	}
	
	result = GetArguments(configValues)
	if not result[0]:
		ctypes.windll.user32.MessageBoxW(0, result[1])
		exit(0)


	pattern = re.compile('[/W_]+') # non-alphanumeric chars
	searchFile = pattern.sub('', configValues['searchfilepath'])

	searchTerms = CleanText(configValues['searchterm'].lower())
	
	# remove unwanted chars from path
	filenameSearchTerms = sanitize_filename(searchTerms.split(' ', 1)[0]) # take first word only
	for c in "' ":
		filenameSearchTerms = filenameSearchTerms.replace(c, "_")


	# set output directory and filename
	outputFilename = f'searchToBrowser_{filenameSearchTerms}.html'
	everythingOutputFilename = f'everything_{filenameSearchTerms}.txt'
	outputPath = os.path.join(OUTPUT_DIRECTORY, outputFilename)
	everythingOutputPath = os.path.join(OUTPUT_DIRECTORY, everythingOutputFilename)
	if not os.path.isdir(OUTPUT_DIRECTORY):
		os.mkdir(OUTPUT_DIRECTORY)

	# delete old output files
	for deleteFile in os.listdir(OUTPUT_DIRECTORY):
		filepath = os.path.join(OUTPUT_DIRECTORY, deleteFile)
		if os.stat(filepath).st_mtime < time() - 1 * 86400 and os.path.isfile(filepath):
			os.remove(filepath)	 


	with open(searchFile, 'r') as f:
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
		smartlistPath = os.path.dirname(os.path.realpath(__file__))
		ctypes.windll.user32.MessageBoxW(0, f'Stale file list: {stringdate}\nReplace SmartList.txt in {smartlistPath}', 'Stale File List')
		pyperclip.copy(smartlistPath)

	foundLines = []
	for readline in searchLines:
		line = CleanText(readline)
		if searchTerms in line.lower() or searchTerms.rstrip() in line.lower() or searchTerms.lstrip() in line.lower():
			foundLines.append(line)
	
	with open(outputPath, 'w') as outfile:
		outfile.write(f'Searching: <a href="file://{searchFile}" target="_new">{searchFile}</a>&nbsp;({str(filedate)[:10]})<br />')
		outfile.write(f'Search Terms: {searchTerms.strip()}<br />')
		outfile.write(f'Found {len(foundLines)} matches in {len(searchLines)} records<br />&nbsp;<br />')
		
		# print a warning if the file searched has 0 records
		if len(searchLines) == 0:
			outfile.write('<p>INVALID</p>')
		else:
			for l in foundLines:
				outfile.write(f'{l}<br />')
	
	# everything output file
	if (len(EVERYTHING_COMMAND_LINE_PATH) > 0):
		command = f'{EVERYTHING_COMMAND_LINE_PATH} -r {searchTerms} > {everythingOutputPath}'
		print(f'everything command: {command}')
		# os.system(command)
		call(command, shell=True) # subprocess.call doesn't open a popup window
		


