# https://ikyle.me/blog/2020/add-mp4-chapters-ffmpeg

import os
import re

print(r'https://ikyle.me/blog/2020/add-mp4-chapters-ffmpeg')
print('ffmpeg -i INPUT.mp4 -i FFMETADATAFILE.txt -map_metadata 1 -codec copy OUTPUT.mp4\r')

chapters = list()

with open('chapters.txt', 'r') as f:
   for line in f:
      x = re.match(r"(\d):(\d{2}):(\d{2}) (.*)", line)
      hrs = int(x.group(1))
      mins = int(x.group(2))
      secs = int(x.group(3))
      title = x.group(4)

      minutes = (hrs * 60) + mins
      seconds = secs + (minutes * 60)
      timestamp = (seconds * 1000)
      chap = {
         "title": title,
         "startTime": timestamp
      }
      chapters.append(chap)

text = ""

for i in range(len(chapters)-1):
   chap = chapters[i]
   title = chap['title']
   start = chap['startTime']
   end = chapters[i+1]['startTime']-1
   text += f"""
[CHAPTER]
TIMEBASE=1/1000
START={start}
END={end}
title={title}
"""

outputFilename = "FFMETADATAFILE"
with open(outputFilename, "a") as myfile:
    myfile.write(text)

print(f'Wrote output file {os.path.abspath(outputFilename)}')