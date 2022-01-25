
from datetime import datetime as dt
import datetime
import Logger
from glob import glob
import os
import re
import shutil
import subprocess
import sys


FILE_AGE_SECONDS = 60 * 60 * 6
LOGFILE_PATH = r'e:\winTvVideos\ProcessOtaVideo.log'
MP4_DESTINATION_ROOT = r'\\andromeda\d\Video'
VIDEO_DIRECTORY = r'e:\WinTvVideos'
VIDEO_INPROCESS_DIRECTORY = r'e:\WinTvVideos\InProcess'

log = Logger.Logger(LOGFILE_PATH)

def GetSubdirName(filename:str) -> str:
    returnVal = str()

    parts = re.split(r'[_\.]', filename)

    for s in parts:
        if len(s) == 8 and (s[:4] == str(dt.now().year) or s[:4] == str(dt.now().year - 1)):
            break
        returnVal += f'{s}_'

    returnVal = returnVal[:(len(returnVal) - 1)]
    returnVal = returnVal.replace(' ', '_')

    return returnVal


def GetTargetFile():
    # find a file that is x hours old
    
    targetFile = str()
    
    for f in glob(os.path.join(VIDEO_DIRECTORY, '*.ts')):
        if (dt.now() - dt.fromtimestamp(os.path.getctime(f))).total_seconds() < FILE_AGE_SECONDS:
            continue
        else:
            targetFile = f
            break
    
    return targetFile






if __name__ == "__main__":
	
    targetFile = GetTargetFile()
    if len(targetFile) == 0: exit(0)  # no file found to be processed
    # targetFile.replace(' ', '_')

    log.AddInfo(f'Processing file {os.path.basename(targetFile)}')

    # move file to work dir
    newFilepath = os.path.join(VIDEO_INPROCESS_DIRECTORY, os.path.basename(targetFile).replace(' ', '_'))
    
    try:
        shutil.move(targetFile, newFilepath)
    except Exception as ex:
        log.AddError(f'Error moving file. {ex}. ({targetFile})')
        exit(1)
    
    tsFile = newFilepath

    # convert from ts to mp4
    mp4Filename =  os.path.splitext(tsFile)[0] + '.mp4'
    
    # ffmpeg -i xxx.ts -c:v libx265 -crf 28 -c:a copy xxx.mp4
    process = subprocess.run(['ffmpeg', '-i', tsFile, '-c:v', 'libx265', '-crf', '28', '-c:a', 'copy', mp4Filename])

    # process = subprocess.run(['ffmpeg', '-i', tsFile, '-c:v', 'libx264', '-c:a', 'ac3', '-b:a', '192k', mp4Filename])

    # this one don't create a viable mp4 file - no video
    # process = subprocess.run(['ffmpeg.exe', '-i', tsFile, '-vcodec', 'libx265', '-crf', '28', mp4Filename])
    
    if process.returncode != 0:
        log.AddError(f'Error executing ffmpeg. {process.stderr}. ({tsFile})')
        exit(1)


    # delete ts file
    try:
        os.remove(tsFile)
    except Exception as ex:
        log.AddError(f'Error deleting file. {ex}. ({tsFile})')


    mp4DestinationDir = MP4_DESTINATION_ROOT

    # check destination dir
    fileRoot = GetSubdirName(os.path.basename(tsFile))
    desiredDir = os.path.join(mp4DestinationDir, 'OTA_' + fileRoot)
    try:
        if len(fileRoot) > 0 and not os.path.isdir(desiredDir):
            os.makedirs(desiredDir)
            mp4DestinationDir = desiredDir
    except Exception as ex:
        log.AddWarning(f'Unable to create directory. {ex}. ({desiredDir})')


    # move file to destination
    mp4DestinationPath = os.path.join(mp4DestinationDir, os.path.basename(mp4Filename))
    try:
        shutil.move(mp4Filename, mp4DestinationPath)
    except Exception as ex:
        log.AddError(f'Unable to move file to {mp4DestinationDir}. {ex} ({mp4Filename})')
        exit(1)

    log.AddInfo(f'Finished processing {os.path.basename(targetFile)}')
