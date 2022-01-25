@echo off
SETLOCAL

SET FFMPEG_PATH=D:\Video\ffmpeg.exe
SET FILE_SIZE_LIMIT=750000000
SET LOGFILE=D:\Video\HandBrakeComplete.log

REM Create dtStamp - "2021-01-14 23:10"
SET HOUR=%time:~0,2%
SET dtStamp9=%date:~-4%-%date:~4,2%-%date:~7,2% 0%time:~1,1%:%time:~3,2% 
SET dtStamp24=%date:~-4%-%date:~4,2%-%date:~7,2% %time:~0,2%:%time:~3,2%
IF "%HOUR:~0,1%"==" " (SET dtStamp=%dtStamp9% -) ELSE (SET dtStamp=%dtStamp24% -)

SET MESSAGE=%dtStamp24% Handbrake completed file. 

REM 2021-12-27 - this block causes the script to crash
REM  IF "%1"=="" (
REM 	SET MESSAGE=%MESSAGE% Received no command line arguments.
REM ECHO cabana
REM pause
REM 	ECHO Usage %0 ^<filename^>
REM  	GOTO Done
REM )
 
ECHO Command Line = %0 %1
REM echo 0.5
REM pause

REM this has got to be a typo
REM SET filepath=%filepath: =_%

REM ::get file info
SET filepath=%1
For %%A in (%filepath%) do (
    REM SET drive=%%~dA
    SET derivedpath=%%~pA
    SET filestem=%%~nA
    REM SET extension=%%~xA
    REM SET datetime=%%~tA
    REM SET size=%%~zA
    REM SET driveandpath=%%~dpA
    SET filename=%%~nxA
)

SET extension=%~x1
SET size=%~z1


REM echo 1 = %1
REM echo derivedpath= %derivedpath%
REM echo extension = %extension%
REM echo filename = %filename%
REM echo filepath = %filepath%
REM echo filestem = %filestem%
REM ECHO size = %size%

REM ::mp4 files only
IF NOT "%extension%" == ".mp4" (
	SET MESSAGE=%MESSAGE% Invalid file type, expected mp4.
	ECHO MP4 files only
	GOTO Done
)

REM ::execute ffmpeg if file is too large
REM ::WARNING: this takes a long time to complete
IF %size% GTR %FILE_SIZE_LIMIT% (
	
	REM losing contents of %MESSAGE% after ffmpeg runs. so write to the log now.
	ECHO %MESSAGE% Found file size %size%, executing ffmpeg. ^(%filepath%^) >> %LOGFILE%
	
	"%FFMPEG_PATH%" -i "%filepath%" -vcodec libx265 -crf 28 "%derivedpath%%filestem%_265.mp4"

	SET HOUR=%time:~0,2%
	SET ffmpegtStamp9=%date:~-4%-%date:~4,2%-%date:~7,2% 0%time:~1,1%:%time:~3,2% 
	SET ffmpegtStamp24=%date:~-4%-%date:~4,2%-%date:~7,2% %time:~0,2%:%time:~3,2%
)

SET filepath=%derivedpath%%filestem%_265.mp4
IF "%HOUR:~0,1%" == " " (SET ffmpegtStamp=%ffmpegtStamp9%) ELSE (SET ffmpegtStamp=%ffmpegtStamp24%)
SET MESSAGE=%ffmpegtStamp% ffmpeg complete 

:Done

ECHO %MESSAGE%
ECHO %MESSAGE% ^(%filepath%^) >> %LOGFILE%
