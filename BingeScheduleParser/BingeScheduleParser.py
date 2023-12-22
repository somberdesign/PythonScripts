from os import listdir, path
import sys
from bs4 import BeautifulSoup


INPUT_FILE_DIRECTORY = path.join(path.dirname(path.realpath(__file__)), 'Input')


def GetInputFiles(directory:str):
	return [f for f in listdir(directory) if path.isfile(path.join(directory, f))]





if __name__ == "__main__":
	for filename in [f for f in listdir(INPUT_FILE_DIRECTORY) if path.isfile(path.join(INPUT_FILE_DIRECTORY, f))]:
		if path.splitext(filename)[1] != 'html':
			next
		fullPathFilename = path.join(INPUT_FILE_DIRECTORY, filename)
		


		fileContents = ''
		try:
			inputDoc = open(fullPathFilename, 'r')
			fileContents = inputDoc.read()
			inputDoc.close()
		except Exception as ex:
			print(f'Error opening file: {ex}. ({fullPathFilename})')
			next


		soup = BeautifulSoup(fileContents, 'html.parser')
		print(soup.prettify())





