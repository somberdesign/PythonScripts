from pymediainfo import MediaInfo
import datetime
import os
import re
import sys
from typing import List, Tuple
import json
from datetime import date

IGNORE_FILENAMES = [
	'.directory.json'
]
JSON_PATH = 'Mp4Validator.json'
NOW = datetime.datetime.now()
WRITE_TO_SCREEN = True

movieDirectories: List[str] = []
outputPathname: str = ''
seriesDirectories: List[str] = []

class SeriesEpisode:
	def __init__(self):
		self.Actors = ''
		self.Artwork = None
		self.Comment = ''
		self.Date = date.min
		self.Director = ''
		self.Episode = -1
		self.Genre = ''
		self.ParentalRating = ''
		self.Rating = -1
		self.Season = -1
		self.SeriesName = ''
		self.Title = ''

	def ReadEpisode(self, fullpath:str):
		
		info = None
		try:
			info = MediaInfo.parse(fullpath)
		except Exception as ex:
			print(f'Error reading {fullPath}')
			return False
		
		print(f'Looking at {fullpath}')
		print(f'found {len(info.tracks)} tracks')

		for track in info.tracks:
			print(f'Track duration = {track.duration}')
			a = 1


		return True

def CheckMovies():

	global IGNORE_FILENAMES
	global movieDirectories
	global NOW
	returnVal = []

	for directory in movieDirectories:
		print(f'Checking {directory}')

		for file in [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]:
			fullPath = os.path.join(directory, file)
			
			if file in IGNORE_FILENAMES:
				continue
			
			if os.path.splitext(file)[1] == '.mp4':
				if (
					len(file) < 10
					or file[-9:-8] != '_'
					or not RepresentsInt(file[-8:-4])
					or int(file[-8:-4]) < 1915
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

					seriesEpisode = SeriesEpisode()
					readSeriesEpisode = seriesEpisode.ReadEpisode(episodeFullPath)
					if not readSeriesEpisode:
						print(f'Error reading {episodeFullPath}')
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


def ReadConfiguration(path):
	global movieDirectories
	global outputPathname
	global seriesDirectories

	REQUIRED_FIELDS = ('movie_directories', 'output_pathname', 'series_directories')
	
	print(f'Reading configuration file {os.path.join(os.path.dirname(os.path.realpath(__file__)), path)}')

	# read file
	data = None
	try:
		with open(path) as json_file:
			data = json.load(json_file)
	except Exception as ex:
		print(f'Exception opening {path}: {ex}')
		return False

	if data is None:
		print(f'Unable to open {path}: {ex}')
		return False

	validData = True

	# set variables
	outputPathname = data['output_pathname']

	if 'movie_directories' in data.keys():
		for d in data['movie_directories']:
			movieDirectories.append(d)
	else:
		print(f'No movie directories found')

	if 'series_directories' in data.keys():
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

	result = ReadConfiguration(JSON_PATH)
	if not result:
		print(f'Error reading json. Exiting')
		sys.exit(1)

	movieMessages = CheckMovies()
	seriesMessages = CheckSeries()
	WriteOutput(movieMessages, seriesMessages)

