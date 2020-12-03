import json
import os
import sys
from twilio.rest import Client

TWILIO_CRED_PATH = r'..\Secrets.json'

account_sid = ''
auth_token = ''

def PrintUsage():
	print('USAGE: py SendSms.py 4075551212 "messsage text"')

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





if __name__ == "__main__":

	if ( len(sys.argv) != 3
		or not RepresentsInt(sys.argv[1])
		or len(sys.argv[1]) != 10
	):
		PrintUsage()
		exit(1)

	result = ReadConfiguration(TWILIO_CRED_PATH)
	if not result: 
		print('Failed to read configuration file. Exiting.')
		exit(1)

	SendMessage(f'+1{sys.argv[1]}', sys.argv[2])



