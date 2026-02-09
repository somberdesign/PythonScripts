copy

=== Create a Movie Sales List ===

1. Download as CSV any Sales sheets that have changed. Save them in dir ~\ReadSalesCsv\Csv_Sales. 
  ..Change the filename to match the following format: 0_Sales-DVDSales2021.csv. 
  ..ALL sales CSVs must be in this dir - none of the info read from them is stored anywhere except the output file, below. 
  ..You only need to replace ones that have changed.

2. Create a new list of movies based on what files are on the drives
  a. Make a new list with "~\FileList\FileList.py". Use SmartList_FULL.txt.
  b. Copy new SmartList_Full.txt to ~\ReadSalesCsv\Input\ as "Movie List.txt" (FILELIST.PY DOES THIS)
  c. Make a copy of SmartList_Full.txt and name it MovieList.txt. Upload this file to Google Drive. (FILELIST.PY DOES THIS)
  d. Copy SmartList_Full to the DVD machine at c:\Users\rgw3\PythonScripts\SearchToBrowser\ as Smartlist_Full.txt:

      copy /y "H:\Users\bob\PythonScripts\FileList\Output\SmartList_full.txt" "c:\Users\rgw3\PythonScripts\SearchToBrowser\Smartlist_Full.txt"

3. Execute ReadSalesCsv.py. This reads data from the csvs and puts it into \Output\SalesData.py.

4. Execute ModifyMovieList.py. This creates MovieList_Sales.html, MovieList_Sales.txt and MovieList_Unmatched.txt in dir \Output.
  .. copy MovieList_Sales.txt to e:\Cached for use by SearchToBrowser.py

      copy /y Output\MovieList_Sales.txt \Cached

  .. print MovieList_Sales.txt for garage sales

      swriter output\MovieList_Sales.txt

NOTE: Series sales stats are at the end of the file

Styles to apply to Movie List.txt before printing:
  .. Format / Page Style / Page / Margins 0.25 each except the Top - make that 1"
  .. Format / Columns / 3
  .. Format / Columns / Separator Line / Style Dotted
  .. Font: Bahnschrift SemiLight 10pt

NOTE: 2b, 2c, and 2d must be done manually if you use the bat file

