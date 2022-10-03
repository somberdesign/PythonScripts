from datetime import date
from glob import glob
from json import load
import Logger
import mutagen
import os
import sys
from typing import List

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

TAG_DICT = {
	'title' : '©nam', 
	'date' : '©day', 
	'series' : 'tvsh', 
	'season' : 'tvsn', 
	'episode' : 'tves', 
	'director' : '©ART', 
	'genre' : '©gen', 
	'rating' : 'rate', 
	'actors' : '----:com.apple.iTunes:ACTORS', 
	'comment' : '©cmt ', 
	'parental-rating' : '----:com.apple.iTunes:PARENTAL RATING', 
	'artwork' : 'covr', 
}

# these values are overwritten if they exist in the config file 
configValues:dict = {
	"script_dir": SCRIPT_DIR,
	"config_file_path": os.path.join(SCRIPT_DIR, '.config.json'),
	"logfile_path": os.path.join(SCRIPT_DIR, 'Mp4MetadataCopy.log'),
}

def ExitScript(exitCode:int, deleteIsRunningFile:bool = True):
	sys.exit(exitCode)

def Get264Files(dirname:str) -> List:
    
	if not os.path.isdir(dirname):
		log.AddError(f'Unable to find dir {dirname}')
		return None

	returnVal = []
	for f in glob(os.path.join(dirname, '*.264.mp4')):
		returnVal.append(f)

	return returnVal


def SetConfigValues(configValues, configFilePath):
	
	# read config values
	f = None
	try:
		f = open(configFilePath, 'r')
	except Exception as ex:
		log.AddError(f'Unable to open config file. {ex}. ({configFilePath})')
		exit(1)

	with f:
		data = None
		try:
			data = load(f)
		except Exception as ex:
			print(f'Error reading config file: {ex}. ({configFilePath})')
			exit(1)

		for i in data:
			if 'comment' in i: continue # skip comments in json
			configValues[i] = data[i]

	# make sure all req'd config values are present
	missingConfigValue = False
	for k in ['file_age_seconds', 'logfile_path', 'mp4_destination_root', 'video_directory', 'video_inprocess_directory']:
		if k not in configValues:
			missingConfigValue = True
			print(f'Missing configuration value: {k}. ({configFilePath})')

	if missingConfigValue:			
		exit(1)


if __name__ == "__main__":


	SetConfigValues(configValues, configValues['config_file_path'])
	log = Logger.Logger(configValues['logfile_path'])

	files264 = Get264Files(configValues['264_directory'])
	if files264 is None:
		log.AddError('Unable to read 264 files. Exiting.')
		ExitScript(1)

	for f in files264:
		
		sourceFile = None
		targetFile = None
		try:
			sourceFile = mutagen.File(f)
		except Exception as ex:
			log.AddError(f'Unable to open file {f}. {ex}.')
			continue

		hevcFilename = f.replace('.264', '')
		try:
			with mutagen.File(hevcFilename, 'r+b') as targetFile:


		except IOError as ex:
			log.AddError(f'Unable to open file {hevcFilename}. {ex}.')
			continue
		
		for k in sourceFile.keys():
			# hevcFilename.set_key(k, sourceFile[k])
			print(f'{k}\t --\t{sourceFile[k]}')

		log.AddInfo(f'Completed metadata copy to file {hevcFilename}')



# https://gist.github.com/lemon24/ebd0b8fa9b223be1948cddc279ea7970



