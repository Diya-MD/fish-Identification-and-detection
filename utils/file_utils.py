"""
utils/file_utils.py
-------------------
Shared file-handling helpers used across routes and services.
"""

from pathlib import Path
from config import ALLOWED_EXT, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB


def get_extension(filename: str) -> str:
    """Return the lowercase extension of *filename* without the leading dot."""
    return Path(filename).suffix.lstrip(".").lower()


def allowed_file(filename: str) -> bool:
    """Return True if *filename* has an extension the app accepts."""
    return get_extension(filename) in ALLOWED_EXT


def is_file_within_size_limit(file) -> bool:
    """
    Return True if *file* does not exceed MAX_FILE_SIZE_BYTES.

    Seeks to the end to read the size, then resets the pointer to 0
    so the file can still be read normally afterwards.
    """
    file.seek(0, 2)                          # seek to end
    size = file.tell()                       # position = size in bytes
    file.seek(0)                             # reset for later reading
    return size <= MAX_FILE_SIZE_BYTES