from os import listdir, path
from re import match
from sys import argv, exit

IS_DEBUG: bool = False
DEFAULT_OUTPUT_FILE_PATH: str = r'c:\temp\ConsecutiveEpisodes.txt'

class Season:
	def __init__(self, seasonNumber:int):
		self.seasonNumber = seasonNumber
		self.episodes = set()

	@property
	def MinEpisode(self) -> int:
		if len(self.episodes) == 0:
			return 0
		return min(self.episodes)	
	
	@property
	def MaxEpisode(self) -> int:
		if len(self.episodes) == 0:
			return 0
		return max(self.episodes)

	def AddEpisode(self, episodeNumber:int):
		self.episodes.add(episodeNumber)

	def GetMissingEpisodes(self) -> list:
		if len(self.episodes) == 0:
			return []

		missingEpisodes = []
		maxEpisode = max(self.episodes)
		for epNum in range(1, maxEpisode + 1):
			if epNum not in self.episodes:
				missingEpisodes.append(epNum)
		return missingEpisodes


def GetSeasonAndEpisode(filename:str) -> tuple[int, int] | None:
	# expected format SxxExx
	matchObj = match(r'.*[sS](\d{2})[eE](\d{2}).*', filename)
	if matchObj is None:
		return None
	
	seasonNumber = int(matchObj.group(1))
	episodeNumber = int(matchObj.group(2))

	return (seasonNumber, episodeNumber)


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
	
	print('USAGE: py ConsecutiveEpisodeCheck.py <sourceDirectory> <outputFile>')

	# verify first param is a diectory
	if argc >= 2 and path.isdir(argv[1]) and path.isdir(argv[1]):
		returnVal['sourceDirectory'] = argv[1]
	else:
		returnVal['sourceDirectory'] = path.abspath(path.dirname(__file__))

	# get output path
	if argc >= 3:
		returnVal['outputFile'] = argv[2]
	else:
		returnVal['outputFile'] = DEFAULT_OUTPUT_FILE_PATH

	print(f'Target Directory: {returnVal["sourceDirectory"]}\nOutput File: {returnVal["outputFile"]}')
	return returnVal



if __name__ == '__main__':
	
	parameters = ProcessCommandLine()

	# read directory contents
	if not path.isdir(parameters['sourceDirectory']):
		print(f'Invalid source directory: {parameters["sourceDirectory"]}')
		exit(1)
	
	files = listdir(parameters['sourceDirectory'])
	seasonDict = {}

	# record seasons and episodes
	for file in files:
		seasonAndEpisode = GetSeasonAndEpisode(file)
		if seasonAndEpisode is None:
			print(f'Unable to parse season and episode from filename: {file}')
			continue

		seasonNumber = seasonAndEpisode[0]
		episodeNumber = seasonAndEpisode[1]

		# if IS_DEBUG:
		# 	print(f'Season: {seasonNumber}, Episode: {episodeNumber}')
	
		# add season if not already present
		if not seasonNumber in seasonDict:
			seasonDict[seasonNumber] = Season(seasonNumber)
		
		# add episode to season
		seasonDict[seasonNumber].AddEpisode(episodeNumber)

	# write output file
	try:
		with open(parameters['outputFile'], 'w') as outputFile:

			outputFile.write('Consecutive Episode Check Report\n')
			outputFile.write(f'Source Directory: {parameters["sourceDirectory"]}\n')
			outputFile.write('===============================\n\n')

			for seasonNumber in sorted(seasonDict.keys()):
				missingEpisodes = seasonDict[seasonNumber].GetMissingEpisodes()
				
				outputFile.write(f'Season {seasonNumber:02d}: Found Episodes {seasonDict[seasonNumber].MinEpisode:02d} to {seasonDict[seasonNumber].MaxEpisode:02d}\n')
				outputFile.write(f'Missing Episodes: {", ".join([f"{epNum:02d}" for epNum in missingEpisodes])}\n')
				outputFile.write('\n')

	except Exception as ex:
		print(f'Error writing output file {parameters["outputFile"]}. {ex}')
		exit(1)

	print(f'\nReport written to {parameters["outputFile"]}\n\n')
	for lines in open(parameters['outputFile'], 'r'):
		print(lines.strip())
