from itertools import permutations
import pyperclip
import random
import re
import sys


KEYWORD_KEEP_ALL_WORDS = 'keepallwords'
KEYWORD_KEEP_PUNCTUATION = 'keeppunctuation'
WORD_LIMIT = 6

keepAllWords = False
removePunctuation = True

def generate_word_permutations(words):
    # Generate all permutations of the words
    word_permutations = permutations(words)
    
    # Convert each permutation tuple to a string
    permutations_as_strings = [' '.join(permutation) for permutation in word_permutations]
    
    return permutations_as_strings


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print('No words')
        exit(0)

    # look for key words and remove dupes
    valid_search_terms = []
    for i in range(1, len(sys.argv)):
        if sys.argv[i].lower().strip() in valid_search_terms:
            continue
        elif sys.argv[i].lower().strip() == KEYWORD_KEEP_ALL_WORDS:
            keepAllWords = True
        elif sys.argv[i].lower().strip() == KEYWORD_KEEP_PUNCTUATION:
            removePunctuation = False
        else:
            valid_search_terms.append(sys.argv[i].lower().strip())

    # remove punctuation
    word_list = []
    for term in valid_search_terms:
        if removePunctuation:
            word_list.append(re.sub("[^A-z0-9]", "", term))
        else:
            word_list.append(term)

    # remove key words
    for word in [KEYWORD_KEEP_ALL_WORDS, KEYWORD_KEEP_PUNCTUATION]:
        while word in word_list:
            word_list.remove(word)

    # remove dead words
    if not keepAllWords:
        for word in ['by', 'the', 'a', 'an', 'to', 'of', 'in', 'my', 'ft', 'and', 'on']:
            while word in word_list:
                word_list.remove(word)

    if len(word_list) > WORD_LIMIT:
        msg = f'Found {len(sys.argv) - 1} words. Limit is {WORD_LIMIT}'
        print(msg)
        pyperclip.copy(msg)
        exit(0)

    result = generate_word_permutations(word_list)

    r = lambda: random.randint(0,255)
    color = '#{:02x}{:02x}{:02x}'.format(r(), r(), r())

    content = ''
    for idx, permutation in enumerate(result, start=1):
        content += permutation + " "

    # heightVal = int(len(content)/850)
    # height = f'"{heightVal}px"'
    # if len(content) > 20000:
    #     height = '25px'
    # if len(content) > 25000:
    #     height = '30px'
    # if len(content) > 30000:
    #     height = '35px'

    # output = f'<div style="color: {color}; background-color: {color}; font-size: 1px; margin: 25px 0px 15px 0px; height: {height}">{content}</div>'
    output = f'<div style="color: {color}; background-color: {color}; font-size: 1px; margin: 25px 0px 15px 0px;">{content}</div>'

    pyperclip.copy(output)
    print(output)
    
