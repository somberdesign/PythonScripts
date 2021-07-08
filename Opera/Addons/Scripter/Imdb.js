 /***
	1. Go to Manage Extension in Opera's Scripter addon and add 
	https://www.imdb.com/* to Site Access / On Specific Sites. 
	
	2. Open an imdb page, click the Scripter addon and include this script in the box.
 
 ***/
 
 
// append new div to this one 
titleDiv = $('[class^=TitleBlock__Container]').first(); 
  
titleParent = $('[class^=TitleBlock__Container]').parent(); 
  
// location of actor names 
starParent = $("a").filter(function() { 
return $(this).text() === "Stars";   
}).parent(); 
  
// make list of genre 
genres = ''; 
genreChips = $('[class^=GenresAndPlot__GenreChip]').each(function(i, obj) { 
genres += $(this).text() + '; '; 
}); 
genres = genres.substr(0, genres.length-2); 
  
// make list of names 
var names = ''; 
starParent.find('a').each(function(i, obj) { 
 
  if (i > 0 && i < 4) { 
   	names += $(this).text() + '; ';  
  } 
  
}); 
names = names.substr(0, names.length-2); 
  
// plot summary 
plotDiv = $('[data-testid=storyline-plot-summary]'); 

// remove —Name  at end of some plots
plot = plotDiv.text(); 
if (plot.lastIndexOf('—') >= 0) {
	plot = plot.substr(0, plot.lastIndexOf('—')); 
}
  
// director 
directorDiv = $('[data-testid=title-pc-principal-credit]').find('a').first(); 
director = directorDiv.text(); 
  
// add new div 
titleParent.prepend( 
  '<div style="padding-right:10px;">' 
  + '<br /><p>' + director + '</p>' 
  + '<br /><p>' + genres + '</p>' 
  + '<br /><p>' + names + '</p>' 
  + '<br /><p>' + plot + '</p>' 
  + '</div><br />&nbsp;<br />' 
); 
  
  
  
  
 
 