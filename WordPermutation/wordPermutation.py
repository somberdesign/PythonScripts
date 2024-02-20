from itertools import permutations
import pyperclip
import random
import re
import sys


WORD_LIMIT = 6

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


    word_list = []
    for i in range(1, len(sys.argv)):
        word_list.append(re.sub("[^A-z0-9]", "", sys.argv[i].lower().strip()))

    
    for w in ['by', 'the', 'a', 'an', 'to', 'of']:
        while w in word_list:
            word_list.remove(w)

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

    height = '10px'
    if len(content) > 31000:
        height = '12px'

    output = f'<div style="color: {color}; background-color: {color}; font-size: 1px; padding: 15px 0px 15px 0px; height: {height}">{content}</div>'

    pyperclip.copy(output)
    print(output)
    
