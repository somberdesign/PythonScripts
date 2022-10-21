 /***
    1. Go to Manage Extension in Opera's Scripter addon and add 
    https://www.imdb.com/* to Site Access / On Specific Sites. 
    
    2. Open an imdb page, click the Scripter addon and include this script in the box.
    
    3. Save changes in the PythonScripts/Opera/Addons/Scripter git project

    4. NOTE: Use spaces instead of tabs. The scripter addon freaks out with tabs.
 
 ***/

function removeA(arr) { 
    var what, a = arguments, L = a.length, ax; 
    while (L > 1 && arr.length) { 
        what = a[--L]; 
        while ((ax= arr.indexOf(what)) !== -1) { 
            arr.splice(ax, 1); 
        } 
    } 
    return arr; 
} 

// adds a "next episode" link above the plot summary div -------------------------
// 2022-10-12 - this is not working
//
aNextEpisode = $('<a>', {
    text: 'Next Episode text',
    title: 'Next Episode',
    href: $("a[title='Next episode']").href
});
aNextEpisode = $('<span>', { text: 'seven plus eight is fifteen' });
let sectionStoryline = $("section[data-testid='Storyline']");
let divNextEpisode = $("<div>", { html: aNextEpisode });
$("section[data-testid='Storyline']").prepend(divNextEpisode);
console.log('executed AddNextEpisodeLink()');
console.log(`divNextEpisode=${divNextEpisode.html()}`);
// -------------------------------------------------------------------------------
  


// append new div to this one  
titleDiv = $('[class^=TitleBlock__Container]').first();  
   
//titleParent = $('[class^=TitleBlock__Container]').parent();  
titleParent = $('.ipc-page-wrapper'); 
  
// location of actor names  
starParent = $("a").filter(function() {  
    return $(this).text() === "Stars";    
}).parent();  
   
// make list of genre  
genreArr = [];  
genreChips = $('[data-testid="genres"]').find('.ipc-chip__text').each(function(i, obj) { 
    genreArr.push($(this).text()); 
});  
  
//create comedy genre names, if needed 
if (genreArr.includes('Comedy')) { 
 
    if (genreArr.includes('Drama')) { 
        genreArr.push('Dramedy'); 
        removeA(genreArr, 'Comedy', 'Drama'); 
    } 
     
    else if (genreArr.includes('Romance')) { 
        genreArr.push('Romantic Comedy'); 
        removeA(genreArr, 'Comedy', 'Romance'); 
    } 
     
    else { 
        var BreakException = {};	 
        targetGenre = ['Crime', 'Action', 'Adult', 'Adventure', 'Animation', 'Family', 'Horror', 'Musical', 'Sci-Fi', 'Sport', 'War', 'Western']; 
        // NOTE: break is not valid in a forEach - must use an exception to exit loop 
        try { 
            targetGenre.forEach(function(item, index) { 
                if (genreArr.includes(item)) { 
                    genreArr.push(item + ' Comedy'); 
                    removeA(genreArr, 'Comedy', item); 
                    throw BreakException; 
                } 
            }); 
        } catch (e) { 
            if (e !== BreakException) throw e; 
            else { 
                console.log('Exception: ' + e.toString()); 
            } 
        } 
    } 
} 
  
genres = genreArr.join('; '); 
  
// make list of names  
var names = '';  
starParent.find('a').each(function(i, obj) {  
  if (i > 0 && i < 4) {  
       names += $(this).text() + '; ';   
  }  
   
});  
names = names.substr(0, names.length-2) + ' ';  

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
  '<div style="padding-right:10px; padding-left:10px">'  
  + '<br /><p>' + director + '</p>'  
  + '<br /><p>' + genres + '</p>'  
  + '<br /><p>' + names + '</p>'  
  + '<br /><p class="plot-summary-top">' + plot + '</p>'  
  + '</div><br />&nbsp;<br />'  
);  
   


// 2022-10-12 - tried to get lazy-loaded plot summary - but this doesn't work
// $(document).on("change", "[data-testid=storyline-plot-summary]", function(e)  {
//     console.log('========  doc change fired');
//     // plot summary  
//     plotDiv = $('[data-testid=storyline-plot-summary]');  
        
//     // remove —Name  at end of some plots 
//     plot = plotDiv.text();  
//     if (plot.lastIndexOf('—') >= 0) { 
//         plot = plot.substr(0, plot.lastIndexOf('—'));  
//     } 

//     $('.plot-summary-top').text(plot);
// })
    
