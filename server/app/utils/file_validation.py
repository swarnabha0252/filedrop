import filetype
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


def _is_valid_text(file: BinaryIO) -> bool:
    try:
        header = file.read(8192)
        file.seek(0)
        header.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _is_webp(header: bytes) -> bool:
    if len(header) < 12:
        return False
    return header[:4] == b"RIFF" and header[8:12] == b"WEBP"


def _is_ole_compound(header: bytes) -> bool:
    return len(header) >= 8 and header[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _is_rar(header: bytes) -> bool:
    return len(header) >= 6 and header[:6] == b"Rar!\x1a\x07"


def _detect_mime_from_header(header: bytes) -> str | None:
    kind = filetype.guess(header)
    if kind is not None:
        return kind.mime

    if _is_webp(header):
        return "image/webp"

    if _is_ole_compound(header):
        return "application/msword"

    if _is_rar(header):
        return "application/x-rar-compressed"

    return None


def validate_mime_type(file: BinaryIO, allowed_types: set) -> str:
    header = file.read(8192)
    file.seek(0)

    detected = _detect_mime_from_header(header)

    if detected is None:
        if _is_valid_text(file):
            detected = "text/plain"
        else:
            raise ValueError("Unable to determine file type")

    if detected not in allowed_types:
        raise ValueError(f"File type '{detected}' is not allowed")
    return detected