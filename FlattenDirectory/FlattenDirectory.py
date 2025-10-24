from os import path, walk
import shutil
from pathlib import Path
from tkinter import messagebox
from sys import argv, exit
from glob import glob
from typing import Tuple, List

def flatten_directory(root_dir):
    root_path = Path(root_dir).resolve()

    # Traverse all files in subdirectories
    for dirpath, dirnames, filenames in walk(root_path, topdown=False):
        current_path = Path(dirpath)
        if current_path == root_path:
            continue  # Skip the root directory itself

        for filename in filenames:
            src_file = current_path / filename
            dst_file = root_path / filename

            # Handle name conflict by appending a number
            counter = 1
            while dst_file.exists():
                dst_file = root_path / f"{src_file.stem}_{counter}{src_file.suffix}"
                counter += 1

            print(f"Moving: {src_file} -> {dst_file}")
            shutil.move(str(src_file), str(dst_file))

        # Remove empty directories
        try:
            current_path.rmdir()
            print(f"Removed empty directory: {current_path}")
        except OSError:
            print(f"Could not remove directory (not empty?): {current_path}")


def GetArguments() -> Tuple[bool, str]:

	# get the number of parameters passed in 
	argc = len(argv)

	# verify the correct number of params 
	# arg[1] = directory to flatten
	if argc < 2:
		return False, 'Usage: FlattenDirectory.py <directory>'

	if not path.isdir(argv[1]):
		return False, f'Error: directory does not exist ({argv[1]})'

	return True, argv[1]

# Example usage
if __name__ == "__main__":
    
	result = GetArguments()
	if not result[0]:
		messagebox.showerror(result[1])
		exit(1)

	flatten_directory(result[1])
