import os
import sys

# Counts the number of files with a specific filetype unsder the target dir

TARGET_FILETYPE = 'url'

if __name__ == '__main__':

	# get the number of parameters passed in
	argc = len(sys.argv)
	
	# verify corrrect number of params
	if argc < 2:
		print('USAGE: py CountFilesPerDir.py <targetDir>')
		exit(1)

	# verify param is an xml file
	targetDir = sys.argv[1]
	if not os.path.isdir(targetDir):
		print(f'Invalid directory ({targetDir})')
		exit(1)

	results = {}
	for dir in [d for d in os.listdir(targetDir) if os.path.isdir(os.path.join(targetDir, d))]:
		filecounter = 0
		testDir = os.path.join(targetDir, dir)
		for f in os.listdir(testDir):
			testItem = os.path.join(targetDir, dir, f)
			if not os.path.isdir(testItem) and os.path.splitext(testItem)[1] == f'.{TARGET_FILETYPE}':
				# print(f)
				if testDir in results.keys():
					results[testDir] += 1
				else:
					results[testDir] = 1
					
	for item in [v[0] for v in sorted(results.items(), key=lambda kv: (-kv[1], kv[0]))]:
		print(f'{item}  {results[item]}')
		
	