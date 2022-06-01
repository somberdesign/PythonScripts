 /***
    1. Go to Manage Extension in Opera's Scripter addon and add 
    https://www.themoviedb.org/* to Site Access / On Specific Sites. 
    
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

// prepend new div to this one  
titleDiv = $('#main');  
   
//titleParent = $('[class^=TitleBlock__Container]').parent();  
titleParent = $('.ipc-page-wrapper'); 
  
// make list of genre  
genreArr = [];  
genreChips = $('span.genres').children('a').each(function(i, obj) { 
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

// rating
rating = '0.0';
ratingClasses = $('.percent').find('span.icon').attr('class').split(/\s+/);
for (i=0; i<ratingClasses.length; i++) {
    if (/icon\-r\d\d/.test(ratingClasses[i])) {
        rating = ratingClasses[i].substring(6,8);
    }
}
  
// make list of names  
names = '';  
$('ol.people.scroller').find('img.profile').each(function(i, obj) {  
  if (i < 3) {  
       names += $(this).attr('alt') + '; ';   
  }  
});  
names = names.substring(0, names.length-2) + ' ';  

// plot summary  
plot = '';
plot = $('.overview').text().trim();  

release = '';
release = $('span.tag.release_date').text().substring(1, $('span.tag.release_date').text().length - 1);
if ($('div.facts > span.release').text().trim().length > 0)
    release = $('div.facts > span.release').text().trim().substring(0, 10);

// director
director = '';
$('li.profile').each(function(i, obj){
    if ($(this).text().includes('Director')) {
        director = $(this).text().substring(0, $(this).text().indexOf('Director')).trim();
        return false; // break out of loop
    }
});


// add new div  
console.log('adding div')
titleDiv.prepend(  
  '<div style="padding-right:10px; padding-left:10px">'
  + '<p>'
  + '<br />' + rating
  + '<br />' + release
  + '<br />' + director   
  + '<br />' + genres   
  + '<br />' + names   
  + '</p>'
  + '<br /><p class="plot-summary-top">' + plot + '</p>'  
  + '</div><br />&nbsp;<br />'  
);  
   
