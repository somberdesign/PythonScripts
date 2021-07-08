@echo off

SET FFMPEG_PATH=D:\Video\ffmpeg.exe
SET FILE_SIZE_LIMIT=1000000000
SET LOGFILE=D:\Video\HandBrakeComplete.log

REM Create dtStamp - "2021-01-14 23:10"
SET HOUR=%time:~0,2%
SET dtStamp9=%date:~-4%-%date:~4,2%-%date:~7,2% 0%time:~1,1%:%time:~3,2% 
SET dtStamp24=%date:~-4%-%date:~4,2%-%date:~7,2% %time:~0,2%:%time:~3,2%
IF "%HOUR:~0,1%" == " " (SET dtStamp=%dtStamp9% -) ELSE (SET dtStamp=%dtStamp24% -)

SET MESSAGE=%dtStamp24% Handbrake completed file. 

REM IF "%1"=="" (
	REM SET MESSAGE=%MESSAGE% Received no command line arguments.
	REM ECHO Usage %0 ^<filename^>
	REM GOTO Done
REM )

REM echo 0.5
REM pause  

REM ::get file info
SET filepath=%1
SET filepath=%filepath: =_%
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


echo 1 = %1
echo derivedpath= %derivedpath%
echo extension = %extension%
echo filename = %filename%
echo filepath = %filepath%
echo filestem = %filestem%
ECHO size = %size%

REM ::mp4 files only
IF NOT "%extension%" == ".mp4" (
	SET MESSAGE=%MESSAGE% Invalid file type, expected mp4.
	ECHO MP4 files only
	GOTO Done
)


REM ::execute ffmpeg if file is too large
REM ::WARNING: this takes a long time to complete
IF %size% GTR %FILE_SIZE_LIMIT% (
	SET MESSAGE=%MESSAGE% Found file size %size%, executing ffmpeg.
	echo "%FFMPEG_PATH%" -i "%filepath%" -vcodec libx265 -crf 28 "%derivedpath%%filestem%_265.mp4"
	"%FFMPEG_PATH%" -i "%filepath%" -vcodec libx265 -crf 28 "%derivedpath%%filestem%_265.mp4"

	SET HOUR=%time:~0,2%
	SET ffmpegtStamp9=0%time:~1,1%:%time:~3,2% 
	SET ffmpegtStamp24=%time:~0,2%:%time:~3,2%
	IF "%HOUR:~0,1%" == " " (SET ffmpegtStamp=%tStamp9% -) ELSE (SET ffmpegtStamp=%tStamp24% -)

	SET MESSAGE=%MESSAGE% ffmpeg complete %ffmpegtStamp%.
	pause
	GOTO Done
)


:Done

ECHO %MESSAGE% ^(%filepath%^) >> %LOGFILE%
REM pause
