


asciiOffsetValue = -96
inWords = ['vingaard', 'dargaard', 'vogler', 'thornwall', 'ironclad', 'solamnic', 'ispin', 'raven']
inWords2 = ['vingaarddargaard', 'voglerthornwall', 'ironcladsolamnic', 'ispinraven']


for word in inWords2:
	for letter in word:
		print(f'{ord(letter) + asciiOffsetValue:02} ', end='')
	print()
	for letter in word:
		print(f'{letter}  ', end='')
	print()
	for i in range(len(word)):
		print('____   ', end='')
	print('\n')




