import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import NamedTuple



class FFProbe:

	class FFProbeResult(NamedTuple):
		return_code: int
		json: str
		error: str
	
	def __init__(self, ffProbeLocation:str, filepath:str):
		self.ffProbeLocation = ffProbeLocation
		self.filepath = filepath


	def __ffprobe__(self) -> FFProbeResult:
		command_array = [self.ffProbeLocation,
			"-v", "quiet",
			"-print_format", "json",
			"-show_format",
			"-show_streams",
			self.filepath]
		result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		return self.FFProbeResult(return_code=result.returncode,
			json=result.stdout,
			error=result.stderr)

	def ffprobe(self):

		ffprobe_result = self.__ffprobe__()
		if ffprobe_result.return_code == 0:
			d = json.loads(ffprobe_result.json)
			streams = d.get("streams", [])
			return streams, str()
			# for stream in streams:
			# 	print(f'{stream.get("codec_type", "unknown")}: {stream.get("codec_long_name")}')

		else:
			return None, str(ffprobe_result.error)

