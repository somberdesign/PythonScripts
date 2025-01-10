@ECHO OFF

rem converts x.264 files to x.265
rem %1 = 264 filename
rem renames input filename *.264.mp4 and creates new file with filename passed in


SETLOCAL
SET TO265_LOGFILE="D:\Video\264 Conversions\To265.log"

REM Create dtStamp - "2021-01-14 23:10"
SET HOUR=%time:~0,2%
SET dtStamp9=%date:~-4%-%date:~4,2%-%date:~7,2% 0%time:~1,1%:%time:~3,2% 
SET dtStamp24=%date:~-4%-%date:~4,2%-%date:~7,2% %time:~0,2%:%time:~3,2%
IF "%HOUR:~0,1%" == " " (SET dtStamp=%dtStamp9% -) ELSE (SET dtStamp=%dtStamp24% -)
ECHO %dtStamp24% Started recode (%1) >> %TO265_LOGFILE%

ren %1 %~n1.264.mp4
SET sourceFilename=%~n1.264.mp4
SET targetFilename=%1

"D:\Video\ffmpeg.exe" -i "%sourceFilename%" -movflags use_metadata_tags -vcodec libx265 -crf 28 "%targetFilename%"


REM Create dtStamp - "2021-01-14 23:10"
SET HOUR=%time:~0,2%
SET dtStamp9=%date:~-4%-%date:~4,2%-%date:~7,2% 0%time:~1,1%:%time:~3,2% 
SET dtStamp24=%date:~-4%-%date:~4,2%-%date:~7,2% %time:~0,2%:%time:~3,2%
IF "%HOUR:~0,1%" == " " (SET dtStamp=%dtStamp9% -) ELSE (SET dtStamp=%dtStamp24% -)
ECHO %dtStamp24% Recode complete (%1) >> %TO265_LOGFILE%


::pause
