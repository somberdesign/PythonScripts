
from datetime import datetime as dt
import datetime
import Logger
from glob import glob
import os
import re
import shutil
import subprocess
import sys


DELETE_SOURCE_FILE_WHEN_COMPLETE = True
FFMPEG_LOCATION = r'c:\ffmpeg\ffmpeg.exe'
FILE_AGE_SECONDS = 60 * 60 * 1
IS_RUNNING_FILENAME = '.seriesconversion'
LOGFILE_PATH = r'D:\Video\264Series\SeriesConversion.log'
MP4_DESTINATION_ROOT = r'd:\Video'
VIDEO_DIRECTORY = r'D:\Video\264Series'
VIDEO_INPROCESS_DIRECTORY = r'D:\Video\264Series\InProcess'

log = Logger.Logger(LOGFILE_PATH)

def GetSubdirName(filename:str) -> str:
    returnVal = str()

    parts = filename.split('_')

    season = int()
    for s in parts:
        if  re.match(r'S\d{2}E\d{2}', s) is not None:  # look for something like "S02E15"
            season = int(s[1:3])
            break
        returnVal += f'{s} '

    returnVal = f'{returnVal}Season {season}'

    return returnVal


def GetTargetFile():
    # find a file that is x hours old
    
    targetFile = str()
    
    files = [os.path.join(VIDEO_DIRECTORY, file) for file in os.listdir(VIDEO_DIRECTORY) if file.lower().endswith('.mp4') or file.lower().endswith('.mp2')]
    files.sort(key=os.path.getmtime)
    # for f in glob(os.path.join(VIDEO_DIRECTORY, '*.mp4')):
    for f in files:
        if (dt.now() - dt.fromtimestamp(os.path.getctime(f))).total_seconds() < FILE_AGE_SECONDS:
            continue
        else:
            targetFile = f
            break
    
    return targetFile






if __name__ == "__main__":

    isRunningPath = os.path.join(os.getcwd(), IS_RUNNING_FILENAME)
    if os.path.isfile(isRunningPath):
        exit(0)
    else:
        f = open(isRunningPath, 'w')
        f.close()
	
    targetFile = GetTargetFile()
    if len(targetFile) == 0: exit(0)  # no file found to be processed
    # targetFile.replace(' ', '_')

    log.AddInfo(f'Processing file {os.path.basename(targetFile)}')

    # move file to work dir
    filestem, ext = os.path.splitext(os.path.basename(targetFile).replace(' ', '_'))
    newFilepath = os.path.join(VIDEO_INPROCESS_DIRECTORY, f'{filestem}.264{ext}')
    
    try:
        shutil.move(targetFile, newFilepath)
    except Exception as ex:
        log.AddError(f'Error moving file. {ex}. ({targetFile})')
        exit(1)
    
    tsFile = newFilepath

    # convert from ts to mp4
    mp4Filename =  tsFile.replace('.264', str())
    
    print(mp4Filename)
    process = subprocess.run([FFMPEG_LOCATION, '-i', f'{tsFile}', '-vcodec', 'libx265', '-crf', '28', f'{mp4Filename}'])

   
    if process.returncode != 0:
        log.AddError(f'Error executing ffmpeg. {process.stderr}. ({tsFile})')
        exit(1)


    # delete source file
    if DELETE_SOURCE_FILE_WHEN_COMPLETE:
        try:
            os.remove(tsFile)
        except Exception as ex:
            log.AddError(f'Error deleting file. {ex}. ({tsFile})')
    else:
        log.AddInfo(f'Did not delete source file. ({tsFile})')


    mp4DestinationDir = MP4_DESTINATION_ROOT

    # check destination dir
    destSubDir = GetSubdirName(os.path.basename(tsFile))
    desiredDir = os.path.join(mp4DestinationDir, destSubDir)
    try:
        if len(destSubDir) > 0 and not os.path.isdir(desiredDir):
            os.makedirs(desiredDir)
    except Exception as ex:
        log.AddWarning(f'Unable to create directory. {ex}. ({desiredDir})')

    if os.path.isdir(desiredDir):
        mp4DestinationDir = desiredDir

    # move file to destination
    mp4DestinationPath = os.path.join(mp4DestinationDir, os.path.basename(mp4Filename))
    try:
        shutil.move(mp4Filename, mp4DestinationPath)
    except Exception as ex:
        log.AddError(f'Unable to move file to {mp4DestinationDir}. {ex} ({mp4Filename})')
        exit(1)

    if os.path.isfile(isRunningPath):
        try:
            os.remove(isRunningPath)
        except Exception as ex:
            log.AddWarning(f'Error deleting file. {ex} ({isRunningPath})')

    log.AddInfo(f'Finished processing {os.path.basename(targetFile)}')
