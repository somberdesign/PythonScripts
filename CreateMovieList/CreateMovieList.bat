@echo off
if ""=="%PYTHONSCRIPTS_PATH%" (
    echo PYTHONSCRIPTS_PATH is not set. Exiting.
    goto END
)

set START_DIRECTORY=%CD%



@REM 1. Download as CSV any Sales sheets that have changed. Save them in dir ~\ReadSalesCsv\Csv_Sales. 
@REM    ..Change the filename to match the following format: 0_Sales-DVDSales2021.csv. 
cd %PYTHONSCRIPTS_PATH%\CreateMovieList
py DownloadSalesCsv.py




@REM 2. Create a new list of movies based on what files are on the drives
@REM   a. Make a new list with "~\FileList\FileList.py". Use *_SmartList_FULL.txt.
cd %PYTHONSCRIPTS_PATH%\FileList
py FileList.py



@REM 3. Execute ReadSalesCsv.py. This reads data from the csvs and puts it into \Output\SalesData.py.
@REM 4. Execute ModifyMovieList.py. This creates MovieList_Sales.html, MovieList_Sales.txt and MovieList_Unmatched.txt in dir \Output.
@REM   .. print MovieList_Sales.txt for garage sales
cd %PYTHONSCRIPTS_PATH%\ReadSalesCsv
py ReadSalesCsv
py ModifyMovieList.py
start "" swriter Output\MovieList_Sales.txt

echo Styles to apply to Movie List.txt before printing:
echo   .. Format / Page Style / Page / Margins 0.25 each
echo   .. Format / Columns / 3
echo   .. Format / Columns / Separator Line / Style Dotted
echo   .. Font 8pt (try Bahnschrift SemiLight 10pt)





:END
cd %START_DIRECTORY%

pause