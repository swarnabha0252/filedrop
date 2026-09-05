import os
from typing import Tuple


def sanitize_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = filename.replace("\\", "").replace("/", "")
    filename = filename.replace("..", "")
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    return filename or "unnamed"


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"