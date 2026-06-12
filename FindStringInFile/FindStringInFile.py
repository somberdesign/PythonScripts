import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox


def main():
    if len(sys.argv) != 3:
        print("Usage: python search_file.py <search_string> <filename>")
        messagebox.showerror("Error", "Invalid arguments. Please provide a search string and a filename.")
        sys.exit(1)

    search_string = sys.argv[1]
    filename = sys.argv[2]

    if not os.path.isfile(filename):
        print(f"File not found: {filename}")
        sys.exit(1)

    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        contents = f.read()

    if search_string.lower() in contents.lower():
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo(
            "String Found",
            f'The string "{search_string}" was found in:\n{filename}'
        )
        root.destroy()
    else:
        # Open the file with the default text editor associated with .txt files
        subprocess.run(['cmd', r'/c', 'subl', filename])
        # subprocess.run(['cmd', 'subl', filename])
        # os.startfile('subl ' + filename)


if __name__ == "__main__":
    main()