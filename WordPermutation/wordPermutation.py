from itertools import permutations
import pyperclip
import sys

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
        word_list.append(sys.argv[i])

    result = generate_word_permutations(word_list)

    # Print the result
    output = "<div style=""color: white"">"
    for idx, permutation in enumerate(result, start=1):
        output += permutation + " "
    output += "</div>"

    pyperclip.copy(output)
    
