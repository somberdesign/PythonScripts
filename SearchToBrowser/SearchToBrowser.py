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
from typing import Tuple, List
from subprocess import call
from easygui import msgbox
from random import choice
from GoogleFonts import GoogleFonts

DIR_TO_SEARCH = r'c:\Users\rgw3\PythonScripts\SearchToBrowser'
OUTPUT_DIRECTORY = r'c:\temp\searchToBrowser'
EVERYTHING_COMMAND_LINE_PATH = r'"C:\Program Files\Everything\es.exe"' # leave empty to disable
SALES_FILE_PATH = r'h:\Cached\MovieList_Sales.txt'
DEBUG = False
IGNORE_FONT_NAMES:List[str] = ['Bigelow Rules', 'Bytesized', 'Comforter', 'Inspiration', 'Jersey 20 Charted', 'Sankofa Display', 'Vina Sans', 'Wavefont']
IGNORE_FONT_STRINGS:List[str] = ['Barcode', 'Yarndings']


def CleanText(line:str) -> str:
	returnVal = re.sub(r'[^A-Za-z0-9 \n\-\~]', str(), line)
	return returnVal
	
def GetArguments(configValues:dict[str, str]) -> Tuple[bool, str]:

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

	searchFileFull = os.path.join(os.path.split(searchFile)[0], os.path.splitext(os.path.split(searchFile)[1])[0] + "_full" + os.path.splitext(os.path.split(searchFile)[1])[1])

	if not os.path.isfile(searchFile) and not os.path.isfile(searchFileFull):
		return False, f'neither {searchFile} nor {searchFileFull} is a file' if len(searchFile) > 0 else f'Unable to find match at {searchFile} or {searchFileFull}'

	configValues['searchfilepath'] = searchFile
	configValues['searchterm'] = sys.argv[2]

	warningMessage = str()
	for v in ['searchfilepath', 'searchterm']:
		if len(configValues[v]) == 0:
			warningMessage += f'SearchToBrowser.GetgArguments(): {v} is not defined\n'

	if len(warningMessage) > 0:
		msgbox(f'WARNING\n{warningMessage}')

	return True, str()

def GetGoogleFontName() -> str:
	
	# fontnames:List[str] = ['Roboto', 'Lora', 'Pacifico', 'Montserrat', 'Raleway', 'Oswald', 'Open', 'Playfair', 'Merriweather', 'Caveat', 'Nunito', 'Abril', 'Comfortaa', 'Indie', 'Anton', 'Quicksand', 'Libre', 'Barlow', 'Exo', 'Arvo', 'Amatic', 'Dancing', 'Josefin', 'Fira', 'Bitter', 'Patua', 'Ubuntu', 'Satisfy', 'Zilla', 'Alegreya', 'Cinzel', 'DM', 'Spectral', 'Shadows', 'PT', 'Slabo', 'Teko', 'Yanone', 'Source', 'Archivo', 'Volkhov', 'Cormorant', 'Cardo', 'Just', 'Francois', 'Fredoka', 'Kaushan', 'Sacremento', 'Chivo', 'Bangers', 'Permanent', 'Crimson', 'Overpass', 'Orbitron', 'Manrope', 'Varela', 'Fjalla', 'Rokkitt', 'Hind', 'Rock', 'Baloo', 'Maven', 'Work', 'Architects', 'Saira', 'Righteous', 'Press', 'Megrim', 'Telex', 'Cantata', 'Staatliches', 'Titan', 'Kumar', 'Economica', 'Averia', 'Noto', 'Yeseva', 'Alice', 'Handlee', 'Mukta', 'Bevan', 'Luckiest', 'Anton', 'Koulen', 'Sen', 'Tangerine', 'Corben', 'Armata', 'Julee', 'Epilogue', 'Special', 'M', 'Lexend', 'Marcellus', 'Asap', 'Vibur', 'Ewert', 'Anonymous', 'Ultra', 'Belanosima']

	fontdata = GoogleFonts.GetGoogleFontData()
	if fontdata is None:
		msgbox('Error receiving google font names')
	else:
		fontnames = []
		for item in fontdata['items']: # type: ignore
			if (
				item not in IGNORE_FONT_NAMES
				and not any(s in item for s in IGNORE_FONT_STRINGS)
			):
				fontnames.append(item['family']); # type: ignore

	
	return choice(fontnames)


def GetSalesFileLines(searchterm:str) -> List[str]:
	returnVal:List[str] = []
	searchLines:List[str] = []

	try:
		with open(SALES_FILE_PATH, 'r') as f:
			searchLines = f.readlines()
	except Exception as ex:
		msgbox(f'ERROR: unable to open sales file ({SALES_FILE_PATH}) ')
		exit(1)

	for line in searchLines:
		result = re.search(r'^\d*\-\d{3}', line)
		if result is not None and searchterm.lower() in line.lower(): # type: ignore
			returnVal.append(line)

	return returnVal



if __name__ == '__main__':

	configValues = {
		'searchfilepath' : str(),
		'searchterm' : str()
	}

	result = GetArguments(configValues)
	if not result[0]:
		ctypes.windll.user32.MessageBoxW(0, result[1])
		exit(0)

	# get sales info
	salesFileLines:List[str] = GetSalesFileLines(configValues['searchterm'])


	pattern = re.compile('[/W_]+') # non-alphanumeric chars
	searchFile = pattern.sub('', configValues['searchfilepath'])

	searchFileFull = os.path.join(os.path.split(searchFile)[0], os.path.splitext(os.path.split(searchFile)[1])[0] + "_full" + os.path.splitext(os.path.split(searchFile)[1])[1])
	if (os.path.exists(searchFileFull)): 
		searchFile = searchFileFull

	if DEBUG:
		msgbox(f'searchFileFull = {searchFileFull}')

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

	if DEBUG:
		msgbox(f'OUTPUT_DIRECTORY = {OUTPUT_DIRECTORY}')

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

	foundLines:List[str] = []
	for readline in searchLines:
		line = CleanText(readline)
		if searchTerms in line.lower() or searchTerms.rstrip() in line.lower() or searchTerms.lstrip() in line.lower():
			foundLines.append(line)
	
	headerCell:str = str()
	catalogCell:str = str()
	salesCell:str = str()

	# print a warning if the file searched has 0 records
	catalogCell += '<h2>Server Catalog</h2>'
	if len(searchLines) == 0:
		catalogCell += '<p>INVALID</p>'
	else:
		for l in foundLines:
			catalogCell += f'{l}<br />'

		# add lines from sales file
		salesCell += '<h2>Sales Data</h2>'
		if len(salesFileLines) > 0:
			for l in salesFileLines:
				salesCell += f'{l}<br />'
		else:
			salesCell += '(no sales data found)'

	googleFontName:str = GetGoogleFontName()



	try:
		with open(outputPath, 'w') as outfile:
			outfile.write(f'<html>')
			outfile.write(f'<head>')
			outfile.write(f'<link rel="stylesheet" href="https://fonts.googleapis.com/css?family={googleFontName}">')
			outfile.write(f'<style>')
			outfile.write(f'body {{ font-family: "{googleFontName}", sans-serif; width: 100% }}')
			outfile.write('td { width: 50%; vertical-align: top; min-width: 500px; }')
			outfile.write(f'</style>')
			outfile.write(f'</head><body>')

			outfile.write(f'Searching: <a href="file://{searchFile}" target="_new">{searchFile}</a>&nbsp;({str(filedate)[:10]})<br />')
			outfile.write(f'Search Terms: {searchTerms.strip()}<br />')
			outfile.write(f'Found {len(foundLines)} matches in {len(searchLines)} records<br />') 
			outfile.write(f'Font Name: {googleFontName}<br />')
			outfile.write(f'&nbsp;<br />')

			outfile.write(f'<table><tr>')
			outfile.write(f'<td>{catalogCell}</td>')
			outfile.write(f'<td>{salesCell}</td>')
			outfile.write(f'</tr></table>')
			outfile.write(f'</body></html>')
	except Exception as ex:
		msgbox(f'Error writing file {outputPath}. {ex}')

				
	# everything output file
	if (len(EVERYTHING_COMMAND_LINE_PATH) > 0):
		command = f'{EVERYTHING_COMMAND_LINE_PATH} -r {searchTerms} > {everythingOutputPath}'
		print(f'everything command: {command}')
		# os.system(command)
		call(command, shell=True) # subprocess.call doesn't open a popup window
		


