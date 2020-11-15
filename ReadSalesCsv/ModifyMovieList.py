# writes file MovieList.html
# Unmatched file list ignors any title with a / in it - don't flag multi-title items


import os
import SalesData # file generated by ReadSalesCsv.py
import datetime
import string

INPUT_FILENAME = r'.\Movie List.txt'
OUTPUT_FILENAME = r'.\MovieList.html'
OUTPUT_FILENAME_UNMATCHED = r'.\MovieList_Unmatched.txt'
FIRST_DATA_LINE = 4
SALESDATA_FILENAME = r'.\SalesData.py'
OUTPUT_COLUMN_COUNT = 1

def MakeEntry(sales, line, matchedKeys):
	
	prefix = ''
	searchkey = line[:len(line)-5].strip() # take year off of the end of the movie name to use as the key
	
	if searchkey in sales.keys():
		matchedKeys.append(searchkey)
		match = sales[searchkey]
		prefix = f'{match[0]}-{match[1]}'
	
	return f'\t<td class="count">{prefix}</td><td class="description">{line}</td>'

def CleanKeys(inDict):
	returnVal = {}
	translator = str.maketrans('', '', string.punctuation)

	for k in inDict.keys():
		if '/' in k: # don't strip multi-title items
			returnVal[k.lower()] = inDict[k]
		else:
			returnVal[k.translate(translator).lower()] = inDict[k]

	return returnVal


def CreateOutputTable(lines, salesDict, matchedKeys):

	lineCounter = 0

	# html header
	output = '<html>\n'
	output += '''
	<style type="text/css">
	\t.count {font-family:monospace;font-size:8px; width:30px; border:0px;}
	\t.description {font-size:10px; border:0px; padding-right:10px;}
	\tTABLE {border:none;border-collapse:collapse;}
	\tTR {border:none;}
	</style>\n
	'''

	output += '<table cellpadding="0" cellspacing="0">\n'

	for line in lines:
		lineCounter += 1
		line = line.strip()

		if lineCounter <= FIRST_DATA_LINE:
			output += (f'\t<tr><td colspan="2" class="description">{line}</td></tr>\n')
			continue

		if lineCounter == FIRST_DATA_LINE + 1:
			output += '\t<tr><td colspan="2">&nbsp;</td></tr>\n'
			output += '</table>\n'
			output += '<table cellpadding="0" cellspacing="0">\n\t<tr>\n'
			continue

		output += f'\t{MakeEntry(salesDict, line, matchedKeys)}\n'
		
		if (lineCounter + FIRST_DATA_LINE) % OUTPUT_COLUMN_COUNT == 0:
			output += '\t</tr><tr>\n'

	output += '</tr></table></html>'
	return output

def ReadMovieList():
	returnVal = []

	with open(INPUT_FILENAME, 'r') as infile:
		lines = infile.readlines()

	for l in lines:
		returnVal.append(l.lower())

	return returnVal

def WriteOutputFile(output):
	try:
		with open(OUTPUT_FILENAME, 'w') as outputFile :
			outputFile.write(output)
	except Exception as ex:
		print(f'Error writing output file {OUTPUT_FILENAME}. {ex}')
		return False

	return True

def WriteUnmatchedFile(salesDict, matchedKeys):
	COL_COUNT = 0
	COL_AMOUNT = 1
	COL_DATES = 2


	outputItems = []
	count_ignore = 0
	count_unmatched = 0
	count_season = 0
	for k in salesDict.keys():

		if any(s in k.lower() for s in ['/', 'replacement disc']): # ignore multi-title items
			count_ignore += 1
			continue 

		if ' season ' in k.lower():
			count_season += 1
			continue

		if k not in matchedKeys: 
			count_unmatched += 1
			outputItems.append(f'{salesDict[k][COL_DATES]}\t{k}\n')
			
	try:	
		with open(OUTPUT_FILENAME_UNMATCHED, 'w') as outputFile:
			outputFile.write(f'# generated {datetime.date.today()}\n\n')
			outputFile.write(f'# found {count_unmatched} unmatched items\n')
			outputFile.write(f'# {count_ignore} items contain ignore strings\n')
			outputFile.write(f'# ignored {count_season} "Season" items\n')
			outputFile.write('\n')
			outputFile.writelines(outputItems)

	except Exception as ex:
		print(f'Error writing unmatched file {OUTPUT_FILENAME_UNMATCHED}')

if __name__ == "__main__":

	salesDict = CleanKeys(SalesData.sales)


	movieListLines = ReadMovieList()
	matchedKeys = []

	output = CreateOutputTable(movieListLines, salesDict, matchedKeys)
	WriteOutputFile(output)
	WriteUnmatchedFile(salesDict, matchedKeys)

