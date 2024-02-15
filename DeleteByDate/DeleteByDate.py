import datetime
import os
import sys


## 2024-02-08
## Currently prints recursive file list of target directory


def GetListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 

    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        
        fullPath = os.path.join(dirName, entry) # Create full path
        
		# If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + GetListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles

def PrintUsage():
	print('USAGE: \npy DeleteByDate.pyw <Directory> [File age in days]\nFile age in days defaults to 180')
     
def RepresentsInt(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False


if __name__ == "__main__":

    if len(sys.argv) < 2:
        PrintUsage()
        exit(1)

    dirPath = sys.argv[1]
    
    fileAge = 180
    if len(sys.argv) > 2:
        if RepresentsInt(sys.argv[2]):
            fileAge = int(sys.argv[2])
        else:
             PrintUsage()
             exit(1)
         
    print(f'DeleteFiles\nPath:{dirPath}\nFile Age: {fileAge}')

    allItems = GetListOfFiles(dirPath)
    for item in allItems:
        print(item)
