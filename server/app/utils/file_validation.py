import magic
from typing import BinaryIO
from app.core.config import settings


def validate_file_size(file: BinaryIO) -> int:
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    
    if size > settings.max_file_size_bytes:
        raise ValueError(f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB")
    if size == 0:
        raise ValueError("File is empty")
    return size


def validate_mime_type(file: BinaryIO, allowed_types: set) -> str:
    header = file.read(8192)
    file.seek(0)
    detected_type = magic.from_buffer(header, mime=True)
    
    if detected_type not in allowed_types:
        raise ValueError(f"File type '{detected_type}' is not allowed")
    return detected_type