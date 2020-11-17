import os
import random
import pyperclip

goodFileExtension = ['.jpg', '.png', '.jpeg']
dir = os.path.dirname(os.path.realpath(__file__))
filename = __file__

while os.path.splitext(filename)[1] not in goodFileExtension:
    filename = random.choice(os.listdir(dir))
    
pyperclip.copy(os.path.join(dir, filename))
