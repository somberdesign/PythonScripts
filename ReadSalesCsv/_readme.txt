

=== Create a Movie Sales List ===

0.9 Open google doc 'Movie List.txt'

1. Download as CSV any Sales sheets that have changed. Save them in dir ~\ReadSalesCsv\Csv_Sales. 
  ..Change the filename to match the following format: 0_Sales-DVDSales2021.csv. 
  ..ALL sales CSVs must be in this dir - none of the info read from them is stored anywhere except the output file, below. 
  ..You only need to replace ones that have changed.

2. Put a current copy of 'Movie List.txt' in dir ~\ReadSalesCsv\Input .
  .. Make a new list with "~\FileList\FileList.py". Use SmartList_*.txt.
  .. Replace the contents of google doc 'Movie List.txt' with what's in SmartList_*.txt

3. Execute ReadSalesCsv.py. This reads data from the csvs and puts it into \Output\SalesData.py.

4. Execute ModifyMovieList.py. This creates MovieList_Sales.html, MovieList_Sales.txt and MovieList_Unmatched.txt in dir \Output.
  .. print MovieList_Sales.txt for garage sales
  .. use swriter MovieList_Sales.txt

NOTE: Series sales stats are at the end of the file

Styles to apply to Movie List.txt before printing:
  .. Format / Page Style / Margins 0.25 each
  .. Format / Columns / 3
  .. Format / Columns / Separator Line / Style Dotted
  .. Font 8pt
