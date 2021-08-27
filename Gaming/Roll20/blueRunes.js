const colorArray = ['BLUE', 'Red', 'Green', 'Yellow'];
var runes = [0, 2, 0, 3, 1];
const triesMax = 15;
var triesLeft = triesMax + 1;


function touchRune(runeIdx) {
    returnVal = '';

	switch(runeIdx) {
		case 0:
			// no action
			returnVal = '\nNo color changes';
		break;
		case 1:
			runes[1] += 1;
			runes[2] += 1;
			runes[3] += 1;
			runes[4] += 1;
			returnVal = '\nRunes B, C, D and E change color!';
		break;
		case 2:
			runes[2] += 1;
			runes[3] += 1;
			runes[4] += 1;
			returnVal = '\nRunes C, D and E change color!';
		break;
		case 3:
			runes[3] += 1;
			returnVal = '\nRune D changes color!';
		break;
		case 4:
			runes[3] += 1;
			runes[4] += 1;
			returnVal = '\nRunes D and E change color!';
		break;
	}
	
	// roll color over from last to first
	for (i=0; i<runes.length; i++)
		if (runes[i] > colorArray.length - 1) runes[i] = 0;
		
	return returnVal;
}

on ('chat:message', function(msg) {

    if (msg.type == 'api' && msg.content.toLowerCase().indexOf('!touchrune') != -1) {
		tokens = msg.content.split(' ');

		// do nothing if no parameter or parameter is not letter A-E
		if (tokens.length < 2 || 'abcde'.indexOf(tokens[1].toLowerCase()) == -1) return 0;
		
		// create output header
		var returnVal = '\n\n=== Touched ' + tokens[1].toUpperCase() + ' ==='
		returnVal += touchRune('abcde'.indexOf(tokens[1].toLowerCase()));
		triesLeft--;
		
		// add rune status to output
		for (i=0; i<runes.length; i++)
			returnVal += '\nRune ' + 'ABCDE'[i] + ': ' + colorArray[runes[i]]
		
		// create tries left graph
		returnVal += '\n' + ('0'.repeat(triesLeft) + '.'.repeat(triesMax)).substr(0, triesMax);
		
		sendChat(msg.who, returnVal);
	}
});

