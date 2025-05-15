::@echo off

:: concatenates all mp4 files in CURRENT DIRECTORY



rem create dir for baseline files
if not exist baseline mkdir baseline

rem create "baseline" copies of files to concat. re-encode because files must all share the same properties.

rem 264 baseline encode
rem for %%f in (*.mp4) do ffmpeg -i %%f -c:v libx264 -profile:v baseline -level:v 3.1 -refs 1 -r 30 -video_track_timescale 90k -filter:v scale="-1:720",pad="1280:720:720/2+ow/2",format="yuv420p" -c:a copy baseline\%%f

rem 265 baseline encode
for %%f in (*.mp4) do ffmpeg -i %%f -movflags use_metadata_tags -vcodec libx265 -vsync cfr -crf 28 -c:a copy baseline\%%f

rem create file list
cd baseline
if exist f del f
for %%f in (*.mp4) do echo file '%%f' >> f

rem concat files
ffmpeg.exe -f concat -safe 0 -i f -c copy ..\concat_output.mp4

rem clean up
cd ..
rmdir baseline /s /q

:END



