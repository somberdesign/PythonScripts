import sys
import os
import csv


class ReadCsv:
	
	def Read(csvPath: str):

		csv_file = None
		returnVal = None
		try:
			csv_file = open(csvPath)
			returnVal = csv.reader(csv_file, delimiter=',')

		except Exception as ex:
			print(f'ERROR: Unable to read {csvpath}. {ex}')
			return None

		for row in returnVal:
			print(row)
		
		csv_file.close()

		return returnVal



