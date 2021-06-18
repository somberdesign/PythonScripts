@echo off

SET FFMPEG_PATH=D:\Video\ffmpeg.exe
SET FILE_SIZE_LIMIT=1000000000
SET LOGFILE=D:\Video\HandBrakeComplete.log

REM Create dtStamp - "2021-01-14 23:10"
SET HOUR=%time:~0,2%
SET dtStamp9=%date:~-4%-%date:~4,2%-%date:~7,2% 0%time:~1,1%:%time:~3,2% 
SET dtStamp24=%date:~-4%-%date:~4,2%-%date:~7,2% %time:~0,2%:%time:~3,2%
IF "%HOUR:~0,1%" == " " (SET dtStamp=%dtStamp9% -) else (SET dtStamp=%dtStamp24% -)

IF "%1"=="" (
	ECHO %dtStamp% Received no command line arguments >> %LOGFILE%
	echo Usage %0 ^<filename^>
	GOTO Done
)

REM get file info
SET filepath=%1
For %%A in ("%filepath%") do (
    SET drive=%%~dA
    SET derivedpath=%%~pA
    SET filestem=%%~nA
    SET extension=%%~xA
    SET datetime=%%~tA
    SET size=%%~zA
    SET driveandpath=%%~dpA
    SET filename=%%~nxA
)

ECHO %dtStamp24% Handbrake completed file. ^(%driveandpath%%filename%^) >> %LOGFILE%

REM mp4 files only
IF NOT "%extension%" == ".mp4" (
	ECHO %dtStamp% Invalid file type. ^(%driveandpath%%filename%^) >> %LOGFILE%
	ECHO MP4 files only
	GOTO Done
)

REM execute ffmpeg if file is too large
IF %size% GTR %FILE_SIZE_LIMIT% (
	ECHO Found file size %size%, executing ffmpeg. ^(%driveandpath%%filename%^) >> %LOGFILE%
	start cmd.exe /c "%FFMPEG_PATH%" -i "%driveandpath%%filename%" -vcodec libx265 -crf 28 "%filestem%_265.mp4"
	GOTO Done
)


:Done
