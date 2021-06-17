import json
import os
import sys
from twilio.rest import Client
import datetime

TWILIO_CRED_PATH = r'..\Secrets.json'
LOGFILE_PATH = 'SendSms.log'

account_sid = ''
auth_token = ''

def GetLastLogDateTime():
	
	lines = None
	try:
		file = open(LOGFILE_PATH, 'r')
		lines = file.readlines()
	except Exception as ex:
		WriteLogEntry(f'Error opening {LOGFILE_PATH} for read. {ex}')
	finally:
		if not file.closed:
			file.close()
			
	lastLogDate = datetime.datetime.min
	for line in lines:
		# 2021-03-09 17:48 - Received 4072565747, Handbrake completed 'D:\Video\Victoria 2016\Victoria_S01E00_Rufus_Sewell.mp4'
		try:
			lastDateString = line.split(' - ')[0]
			lastLogDate = datetime.datetime.strptime(lastDateString, '%Y-%m-%d %H:%M')
		except Exception as ex:
			WriteLogEntry(f'Can\'t get a date from {lastDateString}')
			
	return lastLogDate
	

def PrintUsage():
	print('USAGE: \npy SendSms.py 4075551212 "messsage text"')
	print('or\npy SendSms.py 4075551212 "messsage text" <startTime> <endTime>')

def ReadConfiguration(path):
	global account_sid
	global auth_token

	REQUIRED_FIELDS = ('twilio_auth_token_12513256829', 'twilio_account_sid_12513256829')
	
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
	for f in REQUIRED_FIELDS:
		if f not in data:
			print(f'Required field {f} missing from json')
			validData = False
			
		if not validData: return False

	# set variables
		account_sid = data['twilio_account_sid_12513256829']
		auth_token = data['twilio_auth_token_12513256829']

	return True 

def RepresentsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def SendMessage(destinationNumber, message):
	global account_sid 
	global auth_token
	
	client = Client(account_sid, auth_token)

	message = client.messages \
					.create(
						body=message,
						from_='+12513256829',
						to='+14072565747'
					)

	print(message.sid)

def WriteLogEntry(message: str):
	now = datetime.datetime.now()  

	with open(LOGFILE_PATH, 'a') as log:
		log.write(f'{now:%Y-%m-%d %H:%M} - {message}\n')
		log.close()



if __name__ == "__main__":

	if ( 
			len(sys.argv) not in [3, 5]
			or (   len(sys.argv) == 3
				and (not RepresentsInt(sys.argv[1]) or len(sys.argv[1]) != 10)
			)
			or (   len(sys.argv) == 5
				and (not RepresentsInt(sys.argv[3]) or len(sys.argv[3]) != 4 or not RepresentsInt(sys.argv[4]) or len(sys.argv[4]) != 4)
			)
	):
		PrintUsage()
		exit(1)

	WriteLogEntry(f'Received {sys.argv[1]}, {sys.argv[2]}')

	result = ReadConfiguration(TWILIO_CRED_PATH)
	if not result: 
		m = 'Failed to read configuration file. Exiting.'
		print(m)
		WriteLogEntry(m)
		exit(1)

	# now = datetime.datetime.now()
	# if now.hour > 20 or now.hour < 5:
		# m = 'Late at night! No text sent.'
		# print(m)
		# WriteLogEntry(m)
		# exit(1)

	lastLogDate = GetLastLogDateTime()
	print(f'lastLogDate={lastLogDate}')
	print(f'now={datetime.datetime.now()}')
	minutesDiff = (datetime.datetime.now() - lastLogDate).total_seconds() / 60.0
	print(f'minutesDiff={minutesDiff}')
	
	# 2021-03-13 - Twillio trial ran out - no more free sms!
	if 1 == 0: # lastLogDate == datetime.datetime.min or minutesDiff > 15:
		SendMessage(f'+1{sys.argv[1]}', sys.argv[2])



