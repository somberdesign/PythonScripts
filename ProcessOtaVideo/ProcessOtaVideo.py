
# from curses.ascii import FF
from datetime import datetime as dt
import FFProbe
import json
import Logger
from glob import glob
import os
import re
import shutil
from subprocess import run, PIPE, call
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, '.config.json')
FILE_AGE_SECONDS = 60 * 60 * 4
IS_RUNNING_PATH = os.path.join(SCRIPT_DIR, '.' + os.path.splitext(os.path.basename(__file__))[0])
LOGFILE_PATH = r'd:\winTvVideos\ProcessOtaVideo.log'
MP4_DESTINATION_ROOT = r'\\diplomat\d\Video'
VIDEO_DIRECTORY = r'd:\WinTvVideos'
VIDEO_INPROCESS_DIRECTORY = r'd:\WinTvVideos\InProcess'

configValues:dict = {}

log = Logger.Logger(LOGFILE_PATH)

def AddFilenamePrefix(filepath:str, prefix:str = 'OTA_'):
	if os.path.basename(filepath)[0:len(prefix)] == prefix: return filepath
	return os.path.join(os.path.dirname(filepath), prefix + os.path.basename(filepath))

def GetConfigValues(configValues, configFilePath):
	
	f = None
	try:
		f = open(configFilePath, 'r')
	except Exception as ex:
		log.AddWarning(f'Unable to open config file. {ex}. ({configFilePath})')
		return None

	with f:
		data = json.load(f)
		for i in data:
			configValues[i] = data[i]


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
	if deleteIsRunningFile and os.path.isfile(IS_RUNNING_PATH):
		try:
			os.remove(IS_RUNNING_PATH)
		except Exception as ex:
			log.AddWarning(f'Error deleting file. {ex} ({IS_RUNNING_PATH})')

	sys.exit(exitCode)


def GetTargetFile():
	# find a file that is x hours old
	
	targetFile = str()
	
	for f in glob(os.path.join(VIDEO_DIRECTORY, '*.ts')):
		if (dt.now() - dt.fromtimestamp(os.path.getctime(f))).total_seconds() < FILE_AGE_SECONDS:
			continue
		else:
			targetFile = f
			break
	
	return targetFile


if __name__ == "__main__":

	# exit if one of these is already running
	if os.path.isfile(IS_RUNNING_PATH):
		ExitScript(0, deleteIsRunningFile=False)
	else:
		f = open(IS_RUNNING_PATH, 'w')
		f.write('this file prevents multiple instances of the script from running')
		f.close()


	GetConfigValues(configValues, CONFIG_FILE_PATH)
	
	if 'ffmpeg_path' in configValues:
		ffmpegPath = configValues['ffmpeg_path']
	else:
		log.AddError(f'ffmpeg_path not found in config file ({CONFIG_FILE_PATH})')
		ExitScript(1)
	
	if 'ffprobe_path' in configValues:
		ffprobePath = configValues['ffprobe_path']
	else:
		log.AddError(f'ffprobe_path not found in config file ({CONFIG_FILE_PATH})')
		ExitScript(1)
	
	targetFile = GetTargetFile()

	#############
	# targetFile = r"d:\WinTvVideos\Quincy_ME_20220203_1000.ts"
	#############

	if len(targetFile) == 0: ExitScript(0)  # no file found to be processed

	print(f'{dt.now():%Y-%m-%d %H:%M}')
	log.AddInfo(f'Processing file {os.path.basename(targetFile)}')

	ffprobe = FFProbe.FFProbe(ffprobePath, targetFile)
	streamData = ffprobe.ffprobe()[0][0]

	#############
	# ExitScript(0, deleteIsRunningFile=False)
	#############

	# move file to work dir
	newFilepath = os.path.join(VIDEO_INPROCESS_DIRECTORY, os.path.basename(targetFile).replace(' ', '_'))
	newFilepath = AddFilenamePrefix(newFilepath)
	
	try:
		shutil.move(targetFile, newFilepath)
	except Exception as ex:
		log.AddError(f'Error moving file. {ex}. ({targetFile})')
		ExitScript(1)
	
	tsFile = newFilepath

	# convert from ts to mp4
	mp4Filename =  os.path.splitext(tsFile)[0] + '.mp4'
	mp4Filename = AddFilenamePrefix(mp4Filename)

	# base command arguments
	commandLine = ['ffmpeg', '-y', '-i', tsFile, '-c:v', 'libx265', '-preset', 'slow', '-c:a', 'copy']

	# modify crf for some (high file size) series
	commandLine.append('-crf')
	commandLine.append('26')

	# if 'perry_mason' in tsFile.lower():
	# 	commandLine.append('26')
	# else:
	# 	commandLine.append('22')

	# reduce video dimentions
	# log.AddInfo(f'streamData[height] = {streamData["height"]}')
	if int(streamData['height']) > 480:
		log.AddInfo(f'Resizing video from {streamData["width"]}x{streamData["height"]}')
		commandLine.append('-vf')
		commandLine.append('scale=480:-2')
	
	# add target filename
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


	mp4DestinationDir = MP4_DESTINATION_ROOT

	# check destination dir
	fileRoot = GetSubdirName(os.path.basename(tsFile))
	if len(fileRoot) == 0:
		log.AddWarning(f'Unable to create fileRoot ({tsFile})')

	# create destination dir, if needed
	desiredDir = os.path.join(mp4DestinationDir, fileRoot)
	if len(fileRoot) > 0 and not os.path.isdir(desiredDir):
		try:
			os.makedirs(desiredDir)
		except Exception as ex:
			log.AddWarning(f'Unable to create directory. {ex}. ({desiredDir})')

	if os.path.isdir(desiredDir):
		mp4DestinationDir = desiredDir

	# move file to destination
	mp4DestinationPath = os.path.join(mp4DestinationDir, os.path.basename(mp4Filename))
	try:
		shutil.move(mp4Filename, mp4DestinationPath)
	except Exception as ex:
		log.AddError(f'Unable to move file to {mp4DestinationDir}. {ex} ({mp4Filename})')
		ExitScript(1)

	log.AddInfo(f'Finished processing {os.path.basename(targetFile)}')

	ExitScript(0)
