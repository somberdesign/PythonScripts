from datetime import date, datetime
import os
import re
import sys

# 2022-08-19 08:56 - bwhitley - This script is written to match episode numbers to hours
# when recording the Decades binge on weekends.

BINGE_LENGTH_HOURS = 42
BINGE_START_DATETIME = datetime(2022, 8, 13, 11, 0) # time first episode is broadcast when binge begins
EPISODE_LENGTH_MINUTES = 60 # number of minutes in each episode
START_SEASON = 1 # season number of first broadcast
START_EPISODE = 1 # episode number of first broadcast
SEASON_LENGTHS = [12, 25] # number of episodes in each season

def TimeSlotTable() -> list:
	returnVal = []

	episodeCounter = 1
	for season in range(1, len(SEASON_LENGTHS) + 1):
		while episodeCounter <= SEASON_LENGTHS[season - 1]:
			returnVal.append(f'S{season:02}E{episodeCounter:02}')
			episodeCounter += 1
		episodeCounter = 1

	return returnVal

def ProcessCommandLine() -> list:
	returnVal = [str(), []]
	validArguments = ['countfiles']

	# get the number of parameters passed in
	argc = len(sys.argv)
	
	# verify corrrect number of params
	if argc < 2:
		print('USAGE: py EpisodeEstimator.py <targetDir>')
		exit(1)

	# verify param is an xml file
	targetDir = sys.argv[1]
	if not os.path.isdir(targetDir):
		print(f'Invalid directory ({targetDir})')
		exit(1)

	return [sys.argv[1]]

def StartDateAndTime(filename:str) -> datetime:

	if len(filename) < 21: return datetime.min

	idxStart = re.search(r'\d', filename)
	if idxStart is None: return datetime.min

	# looking for "20220819_0900" part of filename
	dateParts = filename[idxStart.start(): 21].split('_')
	if len(dateParts[0]) != 8 or len(dateParts[1]) != 4: return datetime.min

	returnVal = datetime.min
	try:
		yr = int(dateParts[0][0:4])
		mo = int(dateParts[0][4:6])
		dy = int(dateParts[0][6:8])
		hr = int(dateParts[1][0:2])
		mn = int(dateParts[1][2:4])
		returnVal = datetime(yr, mo, dy, hr, mn)
	except Exception:
		return datetime.min


	return returnVal



if __name__ == '__main__':
	
	currentSeason = START_SEASON
	currentEpisode = START_EPISODE
	totalEpisodeCount = sum(SEASON_LENGTHS)

	targetDir = ProcessCommandLine()[0]

	files = sorted(os.listdir(targetDir))
	if len(files) < 2:
		print(f'Not enough files in dir {targetDir}. Exiting.')
		exit(0)

	baseDt = BINGE_START_DATETIME
	episodeLengthMinutes = EPISODE_LENGTH_MINUTES
	timeslotTable = TimeSlotTable()

	seasonRolloverMultiplier = 0 # used if number of broadcast slots exceed total number of episodes
	for f in files:
		episodeDt = StartDateAndTime(f)
		if episodeDt == datetime.min:
			print(f'WARNING: Can\'t get episode time from file {f}. Skipping it.')
			continue

		minutesFromBase = (episodeDt - baseDt).total_seconds() / 60
		timeSlotsFromBase = int(minutesFromBase / episodeLengthMinutes) - (seasonRolloverMultiplier * totalEpisodeCount)
		
		# go back to season 1 if all the episodes have been shown
		if timeSlotsFromBase >= totalEpisodeCount: 
			timeSlotsFromBase = 1
			seasonRolloverMultiplier += 1

		
		if timeSlotsFromBase >= 0 and timeSlotsFromBase < len(timeslotTable):
			print(f'{timeslotTable[timeSlotsFromBase]}\t{f}')
		else:
			print(f'WARNNG: Invalid timeSlotsFromBase value of {timeSlotsFromBase} for {f}')
		


