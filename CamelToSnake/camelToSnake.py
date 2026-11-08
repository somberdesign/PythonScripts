#!/usr/bin/env python3
"""
Convert CamelCase / PascalCase parts of filenames to underscore-separated form
while preserving original letter case and leaving SxxExx season/episode codes alone.

Example:
  Looney_Tunes_Golden_Collection_S04E42_NutsAndVolts.mp4
  → Looney_Tunes_Golden_Collection_S04E42_Nuts_And_Volts.mp4
"""

import re
import sys
from pathlib import Path


def protect_season_episode(name: str) -> tuple[str, dict[str, str]]:
    """
    Temporarily replace SxxExx (and similar) patterns with placeholders
    so they are not modified by the CamelCase converter.
    """
    placeholders = {}
    counter = 0

    def replacer(match: re.Match) -> str:
        nonlocal counter
        key = f"__SEASON_EP_{counter}__"
        placeholders[key] = match.group(0)
        counter += 1
        return key

    # Matches S01E02, S1E2, s04e42, etc.
    protected = re.sub(r'[Ss]\d{1,2}[Ee]\d{1,3}', replacer, name)
    return protected, placeholders


def restore_season_episode(name: str, placeholders: dict[str, str]) -> str:
    for key, original in placeholders.items():
        name = name.replace(key, original)
    return name


def camel_to_underscore(name: str) -> str:
    """
    Insert underscores before capital letters that start a new word,
    without changing any letter case.
    """
    # Lowercase/digit followed by Uppercase
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    # Sequence of Uppercase letters followed by Uppercase+lowercase
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    return name


def convert_filename(filename: str) -> str:
    path = Path(filename)
    stem = path.stem
    suffix = path.suffix

    # Protect SxxExx patterns
    protected_stem, placeholders = protect_season_episode(stem)

    # Convert CamelCase → underscore form (case preserved)
    new_stem = camel_to_underscore(protected_stem)

    # Restore the original season/episode codes
    new_stem = restore_season_episode(new_stem, placeholders)

    return new_stem + suffix


def rename_files(directory: str | Path, dry_run: bool = True) -> None:
    directory = Path(directory)

    if not directory.is_dir():
        print(f"Error: '{directory}' is not a directory.")
        sys.exit(1)

    files = [f for f in directory.iterdir() if f.is_file()]
    if not files:
        print("No files found.")
        return

    print(f"{'DRY RUN – ' if dry_run else ''}Processing {len(files)} file(s) in: {directory.resolve()}\n")

    for old_path in sorted(files):
        old_name = old_path.name
        new_name = convert_filename(old_name)

        if old_name == new_name:
            print(f"  SKIP  {old_name}")
            continue

        new_path = old_path.with_name(new_name)

        if new_path.exists():
            print(f"  COLLISION  {old_name}  →  {new_name}  (target already exists)")
            continue

        print(f"  {'WOULD RENAME' if dry_run else 'RENAMED'}  {old_name}")
        print(f"             →  {new_name}")

        if not dry_run:
            old_path.rename(new_path)

    if dry_run:
        print("\nThis was a dry run. Re-run with --apply to actually rename the files.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert CamelCase filename parts to underscores (case & SxxExx preserved)"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually rename the files (default is dry-run)",
    )

    args = parser.parse_args()
    rename_files(args.directory, dry_run=not args.apply)