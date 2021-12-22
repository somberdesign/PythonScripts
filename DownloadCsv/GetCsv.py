import os
import shutil
import sys
import DownloadCsv

SheetId = None
TargetDirectory = None

def Usage():
	print('USAGE: GetCsv <googleSheetId> <destinationPath>')

if __name__ == "__main__":

	if len(sys.argv) < 3:
		Usage()
		exit(1)

	if len(sys.argv[1]) != 44:
		print(f'Expected a sheet id with a length of 44. This one is {len(sys.argv[1])}.')
		Usage()
		exit(1)

	if not os.path.isdir(sys.argv[2]):
		print(f'{sys.argv[2]} is not a directory.')
		Usage()
		exit()

	SheetId = sys.argv[1]
	TargetDirectory = sys.argv[2]

	# delete old CSVs
	print(f'Deleting CSV directory: {TargetDirectory}')
	try:
		shutil.rmtree(TargetDirectory)
	except Exception as ex:
		print(f'Unable to delete directory {TargetDirectory}. Exiting. {ex}')
		exit(1)

	params = DownloadCsv.DownloadGoogleCsv.NewInstanceParameters(('sheetid',SheetId), None)
	googleCsvs = DownloadCsv.DownloadGoogleCsv(params)
	googleCsvs.DownloadCsvs(TargetDirectory)
	

