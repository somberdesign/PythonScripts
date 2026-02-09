from datetime import datetime, timedelta, date
import Logger2
from os import makedirs, listdir, remove, stat
from os.path import dirname, join, realpath, isfile
from random import choice
from sys import argv, path
from yaml import safe_load, YAMLError

THIS_FILE_PATH: str = dirname(realpath(__file__))
DEFAULT_LOGFILE_PATH: str = join(r"c:\logs\CreateLinkPage_log.txt")
DEFAULT_OUTPUT_FILE_DIR: str = r'c:\temp\CreateLinkPage'
IS_DEBUG: bool = False

configValues = {'logfile': DEFAULT_LOGFILE_PATH, 'url': str(), 'outputfilename': str(), 'searchargs': []}


def CheckPaths() -> bool:
	returnVal: bool = True

	# verify logfile path
	logfilePath = configValues['logfile']
	logfileDir = dirname(logfilePath)
	if not isfile(logfileDir):
		try:
			makedirs(logfileDir, exist_ok=True)
		except Exception as ex:
			print(f'CreateLinkPage.CheckPaths(): unable to create logfile directory {logfileDir}. {ex}')
			returnVal = False

	# verify output directory
	outputDir = DEFAULT_OUTPUT_FILE_DIR
	if not isfile(outputDir):
		try:
			makedirs(outputDir, exist_ok=True)
		except Exception as ex:
			print(f'CreateLinkPage.CheckPaths(): unable to create output directory {outputDir}. {ex}')
			returnVal = False

	return returnVal

def CreateLinkPage(linkPagePath:str, searchArgs:list[str]) -> bool:
	
	searchArgsStringUrl = '%20'.join(searchArgs)
	searchArgsStringUnderscore = '_'.join(searchArgs)
	styleLinkList = [
		'<link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">', 
		'<link rel="stylesheet" href="https://unpkg.com/mvp.css">', 
		'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/milligram/1.4.1/milligram.min.css">'
	]
	styleLink = styleLinkList[datetime.now().month % len(styleLinkList)]

	with open(linkPagePath, 'w') as f:
		f.write(f'<html>\n<head>\n<title>Link Page</title>\n{styleLink}\n</head>\n<body>\n')
		f.write(f'<h1>Link Page</h1> <h2 style="font-style: italic;">{" ".join(searchArgs)}</h2>\n')
		
		f.write('<table border="0" width="75%"<tr>\n')

		f.write('<tr><td colspan="2"></td></tr>\n')

		f.write('<td valign="top" style="padding-right: 20px;">\n')
		f.write('<h3>DVD / Blu-Ray Links:</h3>\n')
		f.write(f'<a href="https://www.google.com/search?q={searchArgsStringUrl}%20dvd%20cover&-site:ebay.com&tbs=isz:l&hl=en-US&sa=X&biw=1865&bih=970&udm=2" target="_google_{searchArgsStringUnderscore}">Google Large Image Search</a><br />\n')
		f.write(f'<a href="https://www.imdb.com/find?ref_=nv_sr_fn&q={searchArgsStringUrl}&s=all" target="_imdb_{searchArgsStringUnderscore}">IMDb</a><br />\n')
		f.write(f'<a href="https://www.google.com/search?q={searchArgsStringUrl}%20site%3Aimdb.com" target="_imdb_google_{searchArgsStringUnderscore}">IMDb (via Google)</a><br />\n')
		f.write(f'<a href="https://www.justwatch.com/us/search?q={searchArgsStringUrl}" target="_justwatch_{searchArgsStringUnderscore}">JustWatch</a><br />\n')
		f.write('</td>\n')

		f.write('<td valign="top" style="padding-right: 20px;">\n')
		f.write('<h3> CD Links:</h3>\n')
		f.write(f'<a href="https://www.allmusic.com/search/all/{searchArgsStringUrl}" target="_allmusic_{searchArgsStringUnderscore}">AllMusic</a><br />\n')
		f.write(f'<a href="https://www.google.com/search?q={searchArgsStringUrl}%20cd%20cover&-site:ebay.com&tbs=isz:l&hl=en-US&sa=X&biw=1865&bih=970&udm=2" target="_google_{searchArgsStringUnderscore}">Google Large Image Search</a><br />\n')
		f.write('</td>\n')

		f.write('</tr></table>\n')

		f.write('</body>\n</html>\n')
	
	return True

def delete_old_files(directory_path, days_old):
	cutoff_time = datetime.now() - timedelta(days=days_old)
	cutoff_timestamp = cutoff_time.timestamp()

	files_deleted_count = 0
	for filename in listdir(directory_path):
		file_path = join(directory_path, filename)

		if isfile(file_path):
			file_mtime = stat(file_path).st_mtime # modification time

			if file_mtime < cutoff_timestamp:
				try:
					remove(file_path)
					files_deleted_count += 1
				except OSError as e:
					Logger2.AddError(f"  Error deleting file {filename}: {e}")

	Logger2.AddInfo(f"File cleanup complete. Total files deleted: {files_deleted_count}")

def ProcessCommandLine():
	returnVal = {
		'sourceDirectory': str(),
		'outputFile': str(),
	} 

	# get the number of parameters passed in
	argc = len(argv)

	if IS_DEBUG:
		print('\n')
		for i in range(argc):
			print(f'argv[{i}]: {argv[i]}')
		print('\n')
	

	if argc > 1:
		configValues['searchargs'] = argv[1:]
	else:
		print('USAGE: py CreateLinkPage.py <searchArg1> <searchArg2> ... <searchArgN>')




if __name__ == "__main__":
	print(f"CreateLinkPage starting...")
	ProcessCommandLine()
	if not CheckPaths():
		print("CreateLinkPage: path check failed. Exiting...")
		exit(1)

	Logger2.SetLogfilePath(configValues['logfile'])
	outputFileName = ' '.join(configValues['searchargs'][:3]).replace(' ', '_') + '.html'
	configValues['outputfilename'] = join(DEFAULT_OUTPUT_FILE_DIR, outputFileName)

	# delete old output files
	delete_old_files(DEFAULT_OUTPUT_FILE_DIR, 7)

	# create page
	CreateLinkPage(configValues['outputfilename'], configValues['searchargs'])

	msg = f"logfile: {configValues['logfile']}\noutput file: {configValues['outputfilename']}\nsearch args: {' '.join(configValues['searchargs'])}"
	Logger2.AddInfo(msg)

# input("\nCreateLinkPage setup complete. Press Enter to exit...")