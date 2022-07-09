
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
		f = open(filepath, 'w')
	except Exception as ex:
		log.AddError(f'Unable to create IgnoreLengthCheckFile. {ex}. ({filepath})')
		return

	with f:
		f.writeln(f'# {dt.now():%Y-%m-%d %H:%M} - This file created by ProcessOtaVideo')
		f.writeln('# Filenames that appear in this list are not subject to duration validation')
		f.writeln('# Add filenames manually, one per line')
		f.writeln('# After a target file is successfully preocessed ProcessOtaVideo removes it from this file\n\n')

	log.AddInfo(f'Created Ignore Duration Check file. ({filepath})')



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
		if (
			(dt.now() - dt.fromtimestamp(os.path.getctime(f))).total_seconds() < configValues['file_age_seconds']
			or os.path.isfile(GetCopyFlagFilename(f)) # ignore files that are already being copied
			):
			continue
		else:
			targetFile = f
			break
	
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



if __name__ == "__main__":

	SetConfigValues(configValues, configValues['config_file_path'])
	log = Logger.Logger(configValues['logfile_path'])

	# exit if one of these is already running
	if os.path.isfile(configValues['is_running_path']):
		ExitScript(0, deleteIsRunningFile=False)
	else:
		f = open(configValues['is_running_path'], 'w')
		f.write(f'({socket.gethostname()}) this file prevents multiple instances of the script from running')
		f.close()

	# make duration check file
	if not os.path.isfile(configValues['no_duration_check_filename']):
		CreateIgnoreDurationCheckFile(configValues['no_duration_check_filename'])

	# create badfiles directory
	if not os.path.isdir(configValues['bad_files_directory']):
		CreateDirectory(configValues['bad_files_directory'])

		
	targetFile = GetTargetFile()
	if len(targetFile) == 0: ExitScript(0)  # no file found to be processed

	print(f'{dt.now():%Y-%m-%d %H:%M}')
	log.AddInfo(f'Processing file {os.path.basename(targetFile)}')

	#############
	# ExitScript(0, deleteIsRunningFile=False)
	#############

	# move file to work dir
	newFilepath = os.path.join(configValues['video_inprocess_directory'], os.path.basename(targetFile).replace(' ', '_'))
	
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
		streamData = ffprobe.ffprobe()[0][0]


	# base command arguments
	commandLine = ['ffmpeg', '-y', '-i', tsFile, '-c:v', 'libx265', '-preset', 'slow', '-c:a', 'copy']

	# modify crf for some (high file size) series
	commandLine.append('-crf')
	commandLine.append('26')

	# reduce video dimensions
	if streamData is not None:
		
		# skip file if it's a funny size
		if floor(float(streamData["duration"])/60) % 30 != 0:
			newFilepath = os.path.join(configValues['bad_files_directory'], os.path.basename(tsFile))
			note = f'File is {round(float(streamData["duration"])/60, 2)} minutes long. Moved to badfiles directory.'
			MoveFile(tsFile, newFilepath, note)
			ExitScript(0)
			
		# change size, if needed
		if int(streamData['height']) > 480:
			log.AddInfo(f'Resizing video from {streamData["width"]}x{streamData["height"]}')
			commandLine.append('-vf')
			commandLine.append('scale=480:-2')
	
	# add target filename
	mp4Filename =  os.path.splitext(tsFile)[0] + '.mp4'
	commandLine.append(mp4Filename)

	log.AddInfo(f'Executing ffmpeg: {" ".join(commandLine)}')
	returnCode = call(commandLine)

	if returnCode != 0:
		log.AddError(f'Error executing ffmpeg. returnCode={returnCode}. ({tsFile})')
		ExitScript(1)

	
	# if process.returncode != 0:
	# 	stderr = process.stderr
	# 	if stderr is not None and len(stderr) > 200: stderr = stderr[:200] + '...'
	# 	log.AddError(f'Error executing ffmpeg. {stderr}. ({tsFile})')
	# 	ExitScript(1)


	# delete ts file
	try:
		os.remove(tsFile)
	except Exception as ex:
		log.AddError(f'Error deleting file. {ex}. ({tsFile})')


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

	log.AddInfo(f'Finished processing {os.path.basename(targetFile)}')

	ExitScript(0)
