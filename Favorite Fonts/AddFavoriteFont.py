from argparse import ArgumentParser
import re
import tkinter as tk
from tkinter import messagebox


def show_info(message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Add Favorite Font", message)
    root.destroy()


def show_error(message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Add Favorite Font", message)
    root.destroy()


if __name__ == '__main__':

    parser = ArgumentParser(description='Add a font to the FavoriteFonts.html file.')
    parser.add_argument('file_path', type=str, help='Path to the FavoriteFonts.html file.')
    parser.add_argument('new_font', type=str, help='Name of the font to add.')
    args = parser.parse_args()

    file_path = args.file_path
    new_font = args.new_font

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find the fontlist array content
    match = re.search(r'(const fontlist = \[)(.*?)(\];)', content, re.DOTALL)

    if not match:
        show_error("Could not locate fontlist in file.")
        exit(0)

    # Extract, clean, and sort fonts
    prefix, raw_list, suffix = match.groups()
    fonts = [f.strip(" '\"[]") for f in raw_list.split(',') if f.strip(" '\"[]")]

    # 3. Check if font exists
    if new_font in fonts:
        show_info(f"The font '{new_font}' already exists in the list. Exiting.")
        exit(0)

    # 4. Add to list and sort alphabetically
    fonts.append(new_font)
    fonts.sort(key=str.lower)

    # Reconstruct the file content
    # Formatting the list content back into the existing JavaScript array brackets
    formatted_list = "'" + "', '".join(fonts) + "'"

    # 5. Save the modified file
    new_content = content.replace(f"{prefix}{raw_list}{suffix}", f"{prefix}{formatted_list}{suffix}")
    new_content = content.replace(f"{prefix}{raw_list}{suffix}", f"{prefix}{formatted_list}{suffix}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # 6. Success message
    show_info(f"Success: '{new_font}' has been added to the file in alphabetical order.")

# Usage
# update_font_list('FavoriteFonts.html', 'NewFontName')