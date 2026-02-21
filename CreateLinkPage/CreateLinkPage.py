from sys import argv, path
from os.path import abspath, dirname, join, realpath, isfile

path.append(abspath(join(dirname(__file__), '..'))) # add parent directory to path so we can import CommonFunctions
from CommonFunctions import StringToInt # in PythonScripts root directory

from datetime import datetime, timedelta, date
import Logger2
from os import makedirs, listdir, path, remove, stat, walk
from random import choice
from rapidfuzz import process, fuzz
from re import sub
# from random import choice
# from yaml import safe_load, YAMLError

THIS_FILE_PATH: str = dirname(realpath(__file__))
DEFAULT_LOGFILE_PATH: str = join(r"c:\logs\CreateLinkPage_log.txt")
DEFAULT_OUTPUT_FILE_DIR: str = r'c:\temp\CreateLinkPage'
FUZZY_SEARCH_THRESHOLD: int = 70
IMAGE_DIR: str = r'h:\Media\Images\DvdImages'
IS_DEBUG: bool = False
LINK_PAGE_CSS: str = join(THIS_FILE_PATH, 'CreateLinkPage.css')

configValues = {'logfile': DEFAULT_LOGFILE_PATH, 'url': str(), 'outputfilename': str(), 'searchargs': []}


def check_paths() -> bool:
	return_val: bool = True

	# verify logfile path
	logfile_path = configValues['logfile']
	logfile_dir = dirname(logfile_path)
	if not isfile(logfile_dir):
		try:
			makedirs(logfile_dir, exist_ok=True)
		except Exception as ex:
			print(f'CreateLinkPage.CheckPaths(): unable to create logfile directory {logfile_dir}. {ex}')
			return_val = False

	# verify output directory
	output_dir = DEFAULT_OUTPUT_FILE_DIR
	if not isfile(output_dir):
		try:
			makedirs(output_dir, exist_ok=True)
		except Exception as ex:
			print(f'CreateLinkPage.CheckPaths(): unable to create output directory {output_dir}. {ex}')
			return_val = False

	return return_val

def create_link_page(link_page_path:str, search_args:list[str], background_image:str) -> bool:
	
	style_link_list = [
		'<link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">', 
		'<link rel="stylesheet" href="https://unpkg.com/mvp.css">', 
		'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/milligram/1.4.1/milligram.min.css">'
	]
	style_link = style_link_list[datetime.now().month % len(style_link_list)]

	with open(link_page_path, 'w') as f:
		f.write(f'<html>\n<head>\n')
		f.write(f'<title>Link Page</title>\n{style_link}\n')

		if background_image:
			f.write(f'<link rel="stylesheet" href="file:///{LINK_PAGE_CSS.replace("\\", "/")}" />\n')

			f.write(f'<style>\n.background-container::before {{ background-image: url(http://bombcyclone:8123/{background_image}); }}\na:link, a:visited, a:hover, a:active {{ color: black; }}\n</style>\n')

		f.write(f'</head>\n<body>\n')

		f.write(f'<div class="background-container">\n')
		f.write(f'<div class="content">\n')
		f.write(f'<h1>Link Page</h1> <h2 style="font-style: italic;">{" ".join(search_args)}</h2>\n')
		
		f.write('<table border="0" width="75%"<tr>\n')

		f.write('<tr><td colspan="2"></td></tr>\n')

		f.write('<td valign="top" style="padding-right: 20px;">\n')
		f.write('<h3>DVD / Blu-Ray Links:</h3>\n')
		f.write(f'<a href="https://www.imdb.com/find?ref_=nv_sr_fn&q={"%20".join(strip_season_designation(search_args))}&s=all" target="_dvd_imdb_{"_".join(search_args)}" style="font-size:20px;">IMDb</a><br />\n')
		f.write(f'<a href="https://www.ebay.com/sch/i.html?_from=R40&_nkw={"%20".join(search_args)}&+-%28blu%29=&_sacat=617&LH_TitleDesc=0&LH_PrefLoc=1&_fsrp=1&_sop=15&LH_BIN=1&LH_ItemCondition=1000%7C2750&LH_BIN=1&rt=nc&LH_Sold=1" target="_dvd_ebaysolditems_{"_".join(search_args)}">eBay (Sold Items)</a><br />\n')
		f.write(f'<a href="https://www.google.com/search?q={"%20".join(search_args)}%20dvd%20cover&-site:ebay.com&tbs=isz:l&hl=en-US&sa=X&biw=1865&bih=970&udm=2" target="_dvd_googleimage_{"_".join(search_args)}">Google Large Image Search</a><br />\n')
		f.write(f'<a href="https://www.google.com/search?q={"%20".join(strip_season_designation(search_args))}%20site%3Aimdb.com" target="_dvd_imdb_google_{"_".join(search_args)}">IMDb (via Google)</a><br />\n')
		f.write(f'<a href="https://www.justwatch.com/us/search?q={"%20".join(strip_season_designation(search_args))}" target="_dvd_justwatch_{"_".join(search_args)}">JustWatch</a><br />\n')
		f.write(f'<a href="https://www.metacritic.com/search/{"%20".join(strip_season_designation(search_args))}/" target="_dvd_metacritic_{"_".join(search_args)}">Metacritic</a><br />\n')
		f.write('</td>\n')

		f.write('<td valign="top" style="padding-right: 20px;">\n')
		f.write('<h3> CD Links:</h3>\n')
		f.write(f'<a href="https://www.allmusic.com/search/all/{"%20".join(search_args)}" target="_cd_allmusic_{"_".join(search_args)}">AllMusic</a><br />\n')
		f.write(f'<a href="https://www.ebay.com/sch/i.html?_fsrp=1&_from=R40&_nkw={"%20".join(search_args)}&_sacat=176984&LH_BIN=1&_sop=15&LH_PrefLoc=2&rt=nc&LH_Sold=1" target="_cd_ebaysolditems_{"_".join(search_args)}">eBay (Sold Items)</a><br />\n')
		f.write(f'<a href="https://www.google.com/search?q={"%20".join(search_args)}%20cd%20cover&-site:ebay.com&tbs=isz:l&hl=en-US&sa=X&biw=1865&bih=970&udm=2" target="_cd_googleimage_{"_".join(search_args)}">Google Large Image Search</a><br />\n')
		f.write('</td>\n')

		f.write('</tr></table>\n')

		f.write('</div></div>\n')
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

	if files_deleted_count > 0:
		Logger2.AddInfo(f"File cleanup complete. Total files deleted: {files_deleted_count}")


def fuzzy_find_files(directory, keywords, threshold=70):
	# 1. Gather all file paths
	file_list = []
	for root, dirs, files in walk(directory):
		for file in files:
			file_list.append(path.join(root, file))

	# 2. Combine keywords into a single query string for matching
	query = " ".join(keywords)

	# 3. Perform fuzzy search
	# extractMatches returns: (matched_string, score, index)
	results = process.extract(query, file_list, scorer=fuzz.WRatio, limit=10)

	# 4. Filter by threshold
	matched_files = [match for match in results if match[1] >= threshold]
	return matched_files


def strip_season_designation(args:list[str]) -> list[str]:
	if (args and len(args) > 2) and (args[-2] == 'season') and StringToInt(args[-1]) is not None:
		return args[:-2]
	return args

def process_command_line():
	return_val = {
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
		work_args = argv[1:]
		
		# if the last argument is a season number, convert it to "season X" format for better search results
		if work_args[-1][0] == 's' and StringToInt(work_args[-1][1:]) is not None:
			season_string = work_args.pop()
			work_args.extend(['season', season_string[1:]])

		
		configValues['searchargs'] = work_args
	else:
		print('USAGE: py CreateLinkPage.py <searchArg1> <searchArg2> ... <searchArgN>')




if __name__ == "__main__":
	print(f"CreateLinkPage starting...")
	process_command_line()
	if not check_paths():
		print("CreateLinkPage: path check failed. Exiting...")
		exit(1)

	Logger2.SetLogfilePath(configValues['logfile'])

	# generate output filename based on search args
	outputFilenameArgs = []
	for i in range(1,len(argv)):
		outputFilenameArgs.append(sub(r'[^a-zA-Z0-9]+', '', argv[i]))
	numberOfArgsForFilename = min(len(outputFilenameArgs), 3)
	outputFileName = '_'.join(outputFilenameArgs[:numberOfArgsForFilename]) + '.html'
	configValues['outputfilename'] = join(DEFAULT_OUTPUT_FILE_DIR, outputFileName)

	# delete old output files
	delete_old_files(DEFAULT_OUTPUT_FILE_DIR, 1)

	# get background image
	background_image = None
	find_results = fuzzy_find_files(IMAGE_DIR, configValues['searchargs'], threshold=FUZZY_SEARCH_THRESHOLD)
	if find_results:
		candidate = choice(find_results)
		background_image = candidate[0]
		background_image = background_image.replace('\\', '/')
		background_image = background_image.replace('"', '')[9:]

	# create page
	create_link_page(configValues['outputfilename'], configValues['searchargs'], background_image)

	msg = f"logfile: {configValues['logfile']}\noutput file: {configValues['outputfilename']}\nsearch args: {' '.join(configValues['searchargs'])}"
	Logger2.AddInfo(msg)

# input("\nCreateLinkPage setup complete. Press Enter to exit...")