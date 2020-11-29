import pymediainfo
import datetime
import os
import re
import sys
from typing import List, Tuple
import json

JSON_PATH = 'Mp4Validator.json'
NOW = datetime.datetime.now()
WRITE_TO_SCREEN = True

movieDirectories: List[str] = []
outputPathname: str = ''
seriesDirectories: List[str] = []

def CheckMovies():
	global movieDirectories
	global NOW
	returnVal = []

	for directory in movieDirectories:
		print(f'Checking {directory}')

		for file in [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]:
			fullPath = os.path.join(directory, file)
			if os.path.splitext(file)[1] == '.mp4':
				if (
					len(file) < 10
					or file[-9:-8] != '_'
					or not RepresentsInt(file[-8:-4])
					or int(file[-8:-4]) < 1930
					or int(file[-8:-4]) > NOW.year
				):
					returnVal.append(('Invalid year', fullPath))

	return returnVal

def CheckSeries():
	global NOW
	global seriesDirectories

	def GetSeasonAndEpisode(filename):
		pattern = r'.+_(S\d\dE\d\d)'
		result = re.search(pattern, filename)
		if result is None:
			return None
		else:
			return (int(result.group(1)[1:3]), int(result.group(1)[4:])) 


	returnVal: List[Tuple] = []

	for directory in seriesDirectories:
		print(f'Checking {directory}')

		# step through each series
		for seriesDirectory in os.listdir(directory):
			seriesFullPath = os.path.join(directory, seriesDirectory)
			
			if os.path.isfile(seriesFullPath):
				returnVal.append(('File found in top level directory', seriesFullPath))
				continue

			# step through each season of a series
			for seasonDirectory in os.listdir(seriesFullPath):
				seasonFullPath = os.path.join(seriesFullPath, seasonDirectory)
				
				if os.path.isfile(seasonFullPath):
					returnVal.append(('File found in Series directory', seasonFullPath))
					continue

				seasonNumber = seasonDirectory.split()[len(seasonDirectory.split()) - 1]
				if RepresentsInt(seasonNumber):
					seasonNumber = int(seasonNumber)
				else:
					returnVal.append(('Unable to determine season number', seasonFullPath))
					seasonNumber = 0

				# check all episodes in the season
				episodeNumberList = []
				for episode in os.listdir(seasonFullPath):
					episodeFullPath = os.path.join(seasonFullPath, episode)
					
					if os.path.isdir(episodeFullPath):
						returnVal.append(('Directory found in Season directory', episodeFullPath))
						continue

					if os.path.splitext(episode)[1] != '.mp4':
						returnVal.append(('Unexpected filetype', episodeFullPath))
						continue

					seasonEpisode = GetSeasonAndEpisode(episode)

					if seasonEpisode is not None:
						if seasonNumber > 0 and seasonEpisode[0] != seasonNumber:
							returnVal.append(('Season in filename does not match season directory', episodeFullPath))
						
						# make a list of episodes to see if any are missing
						episodeNumberList.append(seasonEpisode[1])

				if len(episodeNumberList) > 1:
					for i in range(min(episodeNumberList), max(episodeNumberList)):
						if i not in episodeNumberList:
							returnVal.append((f'Episode {i} not found', seasonFullPath))

	return returnVal


def ReadJson(path):
	global movieDirectories
	global outputPathname
	global seriesDirectories

	REQUIRED_FIELDS = ('movie_directories', 'output_pathname', 'series_directories')
	
	# read file
	data = None
	try:
		with open(path) as json_file:
			data = json.load(json_file)
	except Exception as ex:
		print(f'Unable to open {path}: {ex}')

	validData = True
	for f in REQUIRED_FIELDS:
		if f not in data:
			print(f'Required field {f} missing from json')
			validData = False

	# set variables
	outputPathname = data['output_pathname']

	for d in data['movie_directories']:
		movieDirectories.append(d)

	for d in data['series_directories']:
		seriesDirectories.append(d)

	return True if validData else False
	
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def WriteOutput(movieMessages, seriesMessages):
	global WRITE_TO_SCREEN

	with open(outputPathname, 'w') as file:
		file.write(f'{str(NOW)[:19]}\n')

		if WRITE_TO_SCREEN: print('\nMovie Messages:')
		file.write(f'\nMovie Messages:\n')
		for m in movieMessages:
			message = f'  {m[0]}: {m[1]}'
			if WRITE_TO_SCREEN: print(message)
			file.write(f'  {message}\n')

		if WRITE_TO_SCREEN: print('\nSeries Messages:')
		file.write(f'\nSeries Messages:\n')
		for m in seriesMessages:
			message = f'  {m[0]}: {m[1]}'
			if WRITE_TO_SCREEN: print(message)
			file.write(f'  {message}\n')

if __name__ == "__main__":

	data = ReadJson(JSON_PATH)
	if not data:
		print(f'Error reading json. Exiting')
		sys.exit(1)

	movieMessages = CheckMovies()
	seriesMessages = CheckSeries()
	WriteOutput(movieMessages, seriesMessages)

