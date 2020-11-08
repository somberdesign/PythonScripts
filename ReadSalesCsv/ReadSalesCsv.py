# Reads CSV files and puts the data into a dictionary in a py file

import csv
import datetime
import glob
import math
import os
import re

DATA_FOLDER = r'.\Data'
OUTPUT_FILE = r'.\SalesData.py'

COL_DATE = 0
COL_PAYMENTRECEIVED = 1
COL_PAYPALFEE = 2
COL_POSTAGE = 3
COL_OTHERCOSTS = 4
COL_DESCRIPTION = 5

def ToFloat(inVal):
	returnVal = re.sub('[^0-9\.]', '', inVal)
	try:
		returnVal = float(returnVal)
	except Exception as ex:
		return None

	return returnVal


files = glob.glob(os.path.join(DATA_FOLDER, '*.csv'))
sales = {}
errorList = []

for file in files:
	
	with open(file) as csv_file:
		
		csv_reader = csv.reader(csv_file, delimiter=',')
		line_count = 0
		for row in csv_reader:
			
			# data starts on line 4
			if line_count < 4:
				line_count += 1
				continue

			if len(row[COL_PAYMENTRECEIVED]) > 0:

				description = row[COL_DESCRIPTION]
				amount = ToFloat(row[COL_PAYMENTRECEIVED])
				date = row[COL_DATE]
				
				# can't convert payment received to float
				if amount is None:
					errorList.append(f'Bad amount: {row[COL_DATE]}\t{row[COL_PAYMENTRECEIVED]}')
					continue

				if description in sales:
					sales[description][0] += 1
					sales[description][1] += amount
					sales[description][2].append(date)
				else:
					sales[description] = [1, amount, [date]]
				
with open(OUTPUT_FILE, "w") as file:
	file.write(f'# This file generated on {datetime.date.today()}\n')
	file.write('# [Count, Total payment received, Description, Dates\n')
	file.write('sales={}\n')
	for key in sales.keys():
		dates = ', '.join(sales[key][2])
		file.write(f'sales["{key}"] = ["{sales[key][0]}", "{math.floor(sales[key][1]):03}", "{dates}"]\n')

	file.write('\nerrors=[]')
	for e in errorList:
		file.write(f'errors.append({e})\n')

