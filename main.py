import argparse
import pathlib
import blake3
import json
import os
import sys
import logging
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm

__version__ = "1.0.0"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def select_directory() -> str:
    root = tk.Tk()
    root.withdraw()
    try:
        return filedialog.askdirectory(title="Select a Directory")
    finally:
        root.destroy()


def select_file() -> str:
    root = tk.Tk()
    root.withdraw()
    try:
        return filedialog.asksaveasfilename(
            title="Save JSON file",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
    finally:
        root.destroy()


def calculate_crc(path: str, *, reading_block_size: int = 8192) -> str | None:
    """Compute BLAKE3 hash of a file."""
    crc = blake3.blake3()
    try:
        with open(path, "rb") as fd:
            for chunk in iter(lambda: fd.read(reading_block_size), b""):
                crc.update(chunk)
    except OSError as err:
        logging.warning(f"Failed to read file: {path} ({err})")
        return None
    return crc.hexdigest()


class FileScanner:
    """Scan files and directories and collect metadata."""

    @staticmethod
    def get_file_info(path: pathlib.Path) -> dict:
        stat_info = path.stat()
        return {
            "type": "file",
            "path": str(path.resolve()),
            "name": path.name,
            "size": stat_info.st_size,
            "creation_time": stat_info.st_ctime,
            "last_modified_time": stat_info.st_mtime,
            "crc": calculate_crc(path),
        }

    @staticmethod
    def get_dir_info(path: pathlib.Path) -> dict:
        stat_info = path.stat()
        entries = list(path.iterdir())
        files = [p for p in entries if p.is_file()]
        dirs = [p for p in entries if p.is_dir()]

        return {
            "type": "directory",
            "path": str(path.resolve()),
            "name": path.name,
            "total_size": sum(f.stat().st_size for f in files),
            "file_count": len(files),
            "subdir_count": len(dirs),
            "creation_time": stat_info.st_ctime,
            "last_modified_time": stat_info.st_mtime,
        }

    def scan(self, path: pathlib.Path) -> dict:
        if path.is_dir():
            return self.get_dir_info(path)
        return self.get_file_info(path)


def collect_data(directory: str, depth: int = 1) -> dict:
    path = pathlib.Path(directory)
    if not path.is_dir():
        logging.error(f"Not a directory: {directory}")
        return {}

    scanner = FileScanner()
    entries = list(path.iterdir())
    result = {}

    for item in tqdm(entries, desc=f"Scanning {path.name}", ncols=80):
        if item.is_file():
            result[item.name] = scanner.scan(item)
        elif depth > 1 and item.is_dir():
            dir_info = scanner.scan(item)
            dir_info["children"] = collect_data(str(item), depth - 1)
            result[item.name] = dir_info

    return result


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan a directory and save file info (including BLAKE3 hash) to a JSON file."
    )
    parser.add_argument(
        "--depth", type=int, default=3, help="Depth of directory scanning."
    )
    parser.add_argument("--dir", type=str, help="Directory to scan.")
    parser.add_argument("--out", type=str, help="Path to save the output JSON file.")
    parser.add_argument("--version", action="store_true", help="Show version and exit.")
    return parser.parse_args()


def main():
    args = parse_cli()

    if args.version:
        print(f"Directory Scanner v{__version__}")
        sys.exit()

    directory = args.dir or select_directory()
    if not directory:
        logging.info("No directory selected. Exiting.")
        sys.exit()

    logging.info(f"Scanning directory: {directory}")
    data = collect_data(directory, depth=args.depth)

    output_path = args.out or select_file()
    if not output_path:
        logging.info("No output file selected. Exiting.")
        sys.exit()

    with open(output_path, "w", encoding="utf-8") as fd:
        json.dump(data, fd, indent=4, ensure_ascii=False)

    logging.info(f"Scan complete. Data saved to: {output_path}")


if __name__ == "__main__":
    main()
