import os
import random
import pyperclip

dir = os.path.dirname(os.path.realpath(__file__))
filename = random.choice(os.listdir(dir))
pyperclip.copy(os.path.join(dir, filename))
