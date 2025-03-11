

=== Create a Movie Sales List ===

1. Download as CSV any Sales sheets that have changed. Save them in dir ~\ReadSalesCsv\Csv_Sales. 
  ..Change the filename to match the following format: 0_Sales-DVDSales2021.csv. 
  ..ALL sales CSVs must be in this dir - none of the info read from them is stored anywhere except the output file, below. 
  ..You only need to replace ones that have changed.

2. Create a new list of movies based on what files are on the drives
  a. Make a new list with "~\FileList\FileList.py". Use *_SmartList.txt.
  b. Copy new SmartList to ~\ReadSalesCsv\Input\ as "Movie List.txt"
  c. Replace google doc SmartList.txt with the new one
  d. Copy *_SmartList_Full to the DVD machine at c:\Users\rgw3\PythonScripts\SearchToBrowser\ as SmartlistFull.txt

3. Execute ReadSalesCsv.py. This reads data from the csvs and puts it into \Output\SalesData.py.

4. Execute ModifyMovieList.py. This creates MovieList_Sales.html, MovieList_Sales.txt and MovieList_Unmatched.txt in dir \Output.
  .. print MovieList_Sales.txt for garage sales
  .. use swriter MovieList_Sales.txt

NOTE: Series sales stats are at the end of the file

Styles to apply to Movie List.txt before printing:
  .. Format / Page Style / Page / Margins 0.25 each
  .. Format / Columns / 3
  .. Format / Columns / Separator Line / Style Dotted
  .. Font 8pt (try Bahnschrift Semilight 10pt)
