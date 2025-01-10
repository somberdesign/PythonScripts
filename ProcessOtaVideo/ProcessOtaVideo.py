
# from curses.ascii import FF
from datetime import datetime as dt
from genericpath import isfile
import FFProbe
import json
import Logger
from math import floor
from glob import glob
import os
import re
import shutil
import socket
from subprocess import run, PIPE, call
import sys

ENABLE_PROCESS_FILES = True # True during normal runs, False when working on script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# these values are overwritten if they exist in the config file 
configValues:dict = {
	"script_dir": SCRIPT_DIR,
	"config_file_path": os.path.join(SCRIPT_DIR, '.config.json'),
	"is_running_path": os.path.join(SCRIPT_DIR, '.' + os.path.splitext(os.path.basename(__file__))[0]),
	"bad_files_directory": os.path.join(SCRIPT_DIR, 'badfiles')
}

def AddFilenamePrefix(filepath:str, prefix:str = 'OTA_'):
	if os.path.basename(filepath)[0:len(prefix)] == prefix: return filepath
	return os.path.join(os.path.dirname(filepath), prefix + os.path.basename(filepath))

def CreateDirectory(dirpath:str) -> bool:
	if os.path.isdir(dirpath):
		log.AddWarning(f'Attempted to create a directory that alread exists. ({dirpath})')
		return False

	result = None
	try:
		result = os.makedirs(dirpath)
	except Exception as ex:
		log.AddError(f'Error creating directory. {ex}. ({dirpath})')
		return False

	return True


def CreateIgnoreDurationCheckFile(filepath:str):
	if isfile(filepath):
		log.AddWarning(f'CreateIgnoreDurationCheckFile() called but file already exists. ({filepath})')
		return

	f = None
	try:
		f = open(filepath, 'r')
		print(f'Using config file {filepath}')
	except Exception as ex:
		log.AddError(f'Unable to create IgnoreLengthCheckFile. {ex}. ({filepath})')
		return

	with f:
		f.write(f'# {dt.now():%Y-%m-%d %H:%M} - This file created by ProcessOtaVideo\n')
		f.write('# Filenames that contain strings that appear in this list are not subject to duration validation\n')
		f.write('# Add case insensitive search strings manually, one per line\n')
		f.write('#\n')
		f.write('# After a file matched by a string is successfully processed, ProcessOtaVideo removes the string from this file.\n')
		f.write('# Begin a string with the "+" symbol to disable this behavior and make it persist. Ex: "+Seinfeld" will not be deleted.\n')

	log.AddInfo(f'Created Ignore Duration Check file. ({filepath})')


def GetSubdirName(filename:str) -> str:
	returnVal = str()

	parts = re.split(r'[_\.]', filename)

	for s in parts:
		if len(s) == 8 and (s[:4] == str(dt.now().year) or s[:4] == str(dt.now().year - 1)):
			break
		returnVal += f'{s}_'

	returnVal = returnVal[:(len(returnVal) - 1)]
	returnVal = returnVal.replace(' ', '_')

	return returnVal

def ExitScript(exitCode:int, deleteIsRunningFile:bool = True):
	if deleteIsRunningFile and os.path.isfile(configValues['is_running_path']):
		try:
			os.remove(configValues['is_running_path'])
		except Exception as ex:
			log.AddWarning(f'Error deleting file. {ex} ({configValues["is_running_path"]})')

	sys.exit(exitCode)

def GetCopyFlagFilename(path:str) -> str:
	targetDirectory = os.path.dirname(path)
	copyflag = '.' + os.path.splitext(os.path.basename(path))[0]
	return os.path.join(targetDirectory, copyflag)

def GetTargetFile():
	# find a file that is x hours old
	
	targetFile = str()
	
	for f in glob(os.path.join(configValues['video_directory'], '*.ts')):
		print(f'{f}\n{(dt.now() - dt.fromtimestamp(os.path.getctime(f))).total_seconds()} and {configValues["file_age_seconds"]}')
		if (
			(dt.now() - dt.fromtimestamp(os.path.getctime(f))).total_seconds() < configValues['file_age_seconds']
			or os.path.isfile(GetCopyFlagFilename(f)) # ignore files that are already being copied
			or "1stAttempt" in f # WinTV sometimes leaves some aborted files with this filename
			):
			continue
		else:
			targetFile = f
			break
	
	if len(targetFile) == 0:
		print(f'Unable to find target file at {configValues["video_directory"]}')
	
	return targetFile

def MoveFile(filePath:str, destinationPath:str, note:str = '') -> bool:

	try:
		os.rename(filePath, destinationPath)
	except Exception as ex:
		log.AddError(f'Failed to move file {filePath} to {destinationPath}. {ex}')
		return False

	message = str()
	if len(note) > 0: message += f'{note}. '
	log.AddInfo(f'{message}Moved file {filePath} to {destinationPath}.')

	return True

def ReadNoDurationCheckStrings(noDurationFilepath:str) -> list:
	matchList = []
	
	f = None
	try:
		f = open(noDurationFilepath, 'r')
	except Exception as ex:
		log.AddError(f'Unable to open config file. {ex}. ({noDurationFilepath})')
		return []

	with f:
		for line in f:
			commentPos = line.find('#') 
			if commentPos == -1: matchList.append((line.strip(), False)) # no comment on line
			if commentPos > 0: matchList.append((line[:commentPos].strip(), False)) # ignore lines that begin with #, only read to first # in string

	finalMatchList = []
	for s in matchList:
		if len(s[0]) == 0: continue # remove items with empty strings
		
		if s[0][0] == '+':
			finalMatchList.append((s[0][1:].lower(), True)) # if + at start of line, remove it and set Persist to True
		else:
			finalMatchList.append((s[0].lower(), False))

	return finalMatchList

def RemoveDurationCheckItem(noDurationFilepath:str, itemName:str) -> bool:
	f = None
	try:
		f = open(noDurationFilepath, 'r')
	except Exception as ex:
		log.AddError(f'RemoveDurationCheckItem(): Unable to open config file. {ex}. ({noDurationFilepath})')
		return False

	lines = None
	with f:
		lines = f.readlines()
		lines = [line.rstrip().lower() for line in lines]
	f.close()

	try:
		f = open(noDurationFilepath, 'w')
	except Exception as ex:
		log.AddError(f'RemoveDurationCheckItem(): Unable to open file to write. {ex}. ({noDurationFilepath})')
		return False

	with f:
		for line in lines:
			if line == itemName:
				log.AddInfo(f'Removed item {line} from nodurationcheck file. ({noDurationFilepath})')
			else:
				f.write(f'{line}\n')

	return True

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
			data = json.load(f)
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
	print(f'logfile at {configValues["logfile_path"]}')

	# exit if one of these is already running
	if ENABLE_PROCESS_FILES:
		if os.path.isfile(configValues['is_running_path']):
			print(f'{configValues["is_running_path"]} exists, one instance is already running. Exiting.')
			ExitScript(0, deleteIsRunningFile=False)
		else:
			f = open(configValues['is_running_path'], 'w')
			f.write(f'({socket.gethostname()}) this file prevents multiple instances of the script from running')
			f.close()

	# make duration check file
	if not os.path.isfile(configValues['no_duration_check_filename']):
		CreateIgnoreDurationCheckFile(configValues['no_duration_check_filename'])

	NoDurationCheckItems = ReadNoDurationCheckStrings(configValues['no_duration_check_filename'])

	# create badfiles directory
	if not os.path.isdir(configValues['bad_files_directory']):
		CreateDirectory(configValues['bad_files_directory'])

		
	targetFile = GetTargetFile()
	if len(targetFile) == 0:
		print(f'Could not find target file. Exiting.')
		ExitScript(0)  # no file found to be processed

	print(f'{dt.now():%Y-%m-%d %H:%M}')
	message = f'Processing file {os.path.basename(targetFile)}'
	if not ENABLE_PROCESS_FILES: 
		message = f'TEST TEST {message} TEST TEST'
	log.AddInfo(message)

	#############
	# ExitScript(0, deleteIsRunningFile=False)
	#############

	# move ts file to work dir
	newFilepath = os.path.join(configValues['video_inprocess_directory'], os.path.basename(targetFile).replace(' ', '_'))
	
	if not ENABLE_PROCESS_FILES:
		log.AddInfo('ENABLE_PROCESS_FILES is False. Exiting script.')
		ExitScript(0, False)

	copyFlagFilename = GetCopyFlagFilename(targetFile) # mark this file as being copied - for slow network connections
	if not os.path.isfile(copyFlagFilename):
		try:
			f = open(copyFlagFilename, 'w')
			f.write(f'({socket.gethostname()}) this file prevents multiple instances of the script from copying the same file at the same time')
		except Exception as ex:
			log.AddWarning(f'Error creating file. {ex} ({copyFlagFilename})')
		finally:
			f.close()

	try:
		shutil.move(targetFile, newFilepath)
	except Exception as ex:
		log.AddError(f'Error moving file. {ex}. ({targetFile})')
		ExitScript(1)


	# message = f'Moved file {targetFile}. Exiting.'
	# log.AddInfo(message)
	# ExitScript(0)


	# file successfully moved, remove copy flag
	if os.path.isfile(copyFlagFilename):
		try:
			os.remove(copyFlagFilename)
		except Exception as ex:
			log.AddWarning(f'Error deleting file. {ex} ({copyFlagFilename})')


	tsFile = newFilepath
	ffprobe = FFProbe.FFProbe(configValues['ffprobe_path'], tsFile)
	streamData = None
	if ffprobe.ffprobe()[0]	is None:
		log.AddInfo(f'ffprobe is unable to read file {tsFile}')
	else:
		try:
			streamData = ffprobe.ffprobe()[0][0]
		except Exception as ex:
			log.AddWarning(f'ffprobe error: {ex}. ({tsFile})')
			newFilepath = os.path.join(configValues['bad_files_directory'], os.path.basename(tsFile))
			note = f'ffprobe encountered an error reading this file'
			MoveFile(tsFile, newFilepath, note)
			ExitScript(1)


	# base command arguments
	commandLine = ['ffmpeg', '-y', '-i', tsFile, '-c:v', 'libx265', '-preset', 'slow', '-c:a', 'copy']

	# modify crf for some (high file size) series
	commandLine.append('-crf')
	commandLine.append('26')

	if streamData is not None:
		
		# see if filename is in nodurationcheck file
		performDurationCheck = True
		for i in NoDurationCheckItems:
			if i[0].lower() in os.path.basename(tsFile).lower():
				performDurationCheck = False
				log.AddInfo(f'Found {i[0]} in no duration check file. Disabled duration check. ({os.path.basename(tsFile)})')
				
				# remove item from nodurationcheck file if persist is not set
				if not i[1]:
					RemoveDurationCheckItem(configValues['no_duration_check_filename'], i[0])

				break

		# skip file if it's not an increment of 30 or 1 less than an increment of 30
		floorDuration = floor(float(streamData["duration"]) / 60)
		print(f'floorDuration = {floorDuration}')
		if performDurationCheck and floorDuration % 30 not in [0, 29]:
			newFilepath = os.path.join(configValues['bad_files_directory'], os.path.basename(tsFile))
			note = f'File is {round(float(streamData["duration"])/60, 2)} minutes long. Moved to badfiles directory.'
			MoveFile(tsFile, newFilepath, note)
			ExitScript(0)
			
		# reduce vido dimensions, if needed
		if int(streamData['height']) > 480:
			log.AddInfo(f'Resizing video from {streamData["width"]}x{streamData["height"]}')
			commandLine.append('-vf')
			commandLine.append('scale=480:-2')
	
	# add target filename
	mp4Filename =  os.path.splitext(tsFile)[0] + '.mp4'
	commandLine.append(mp4Filename)

	log.AddInfo(f'Executing ffmpeg: {" ".join(commandLine)}')
	returnCode = None
	try:
		returnCode = call(commandLine)
	except Exception as ex:
		log.AddError(f'Error converting file. {ex}. ({tsFile})')


	if returnCode != 0:
		log.AddError(f'Error executing ffmpeg. returnCode={returnCode}. ({tsFile})')
		ExitScript(1)

	# delete ts file
	try:
		os.remove(tsFile)
	except Exception as ex:
		log.AddError(f'Error deleting file. {ex}. ({tsFile})')
		newFilepath = os.path.join(configValues['bad_files_directory'], os.path.basename(tsFile))
		note = f'Moved file to badfiles directory ({newFilepath})'
		MoveFile(tsFile, newFilepath, note)
		ExitScript(0)


	mp4DestinationDir = configValues['mp4_destination_root']

	# check destination dir
	fileRoot = GetSubdirName(os.path.basename(tsFile))
	if len(fileRoot) == 0:
		log.AddWarning(f'Unable to make fileRoot name ({tsFile})')
	fileRoot = 'OTA_' + fileRoot

	# create destination dir, if needed
	mp4DestinationDir = os.path.join(mp4DestinationDir, fileRoot)
	if len(fileRoot) > 0 and not os.path.isdir(mp4DestinationDir):
		try:
			os.makedirs(mp4DestinationDir)
		except Exception as ex:
			log.AddWarning(f'Unable to create directory. {ex}. ({mp4DestinationDir})')

	# move file to destination
	mp4DestinationPath = os.path.join(mp4DestinationDir, os.path.basename(mp4Filename))
	try:
		shutil.move(mp4Filename, mp4DestinationPath)
	except Exception as ex:
		log.AddError(f'Unable to move file to {mp4DestinationDir}. {ex} ({mp4Filename})')
		ExitScript(1)

	log.AddInfo(f'Moved file to {mp4DestinationPath}')
	log.AddInfo(f'Finished processing {os.path.basename(targetFile)}')

	ExitScript(0)
