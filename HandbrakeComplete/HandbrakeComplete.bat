@echo off
SETLOCAL

SET FFMPEG_PATH=D:\Video\ffmpeg.exe
SET FILE_SIZE_LIMIT=750000000
SET LOGFILE=D:\Video\_HandBrakeComplete.log

REM Create dtStamp - "2021-01-14 23:10"
SET HOUR=%time:~0,2%
SET dtStamp9=%date:~-4%-%date:~4,2%-%date:~7,2% 0%time:~1,1%:%time:~3,2% 
SET dtStamp24=%date:~-4%-%date:~4,2%-%date:~7,2% %time:~0,2%:%time:~3,2%
IF "%HOUR:~0,1%"==" " (SET dtStamp=%dtStamp9% -) ELSE (SET dtStamp=%dtStamp24% -)

SET MESSAGE=%dtStamp24% Handbrake completed file. 

 
ECHO Command Line = %0 %1 %2 %3
SET filepath=%1
SET sourcePath=%2
SET exitCode=%3

REM ::get file info
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



:Done

ECHO %MESSAGE% ^(\[%exitCode%\] %sourcePath% -^> %filepath%^) >> %LOGFILE%
pause
