import sys
import os
import csv


class ReadCsv:
	
	def Read(csvPath: str):

		returnVal = []
		try:
			csv_file = open(csvPath)
			reader = csv.reader(csv_file, delimiter=',')


			for r in reader:
				returnVal.append(r)

			csv_file.close()

		except Exception as ex:
			print(f'ERROR: Unable to read {csvPath}. {ex}')
			return None
		

		return returnVal



