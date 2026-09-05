import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional


class StorageService(ABC):
    @abstractmethod
    async def upload(self, key: str, file: BinaryIO) -> None:
        pass

    @abstractmethod
    async def download(self, key: str) -> Optional[BinaryIO]:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    async def get_file_path(self, key: str) -> Optional[str]:
        pass


class LocalStorageService(StorageService):
    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, key: str) -> Path:
        safe_key = key.replace("..", "").lstrip("/\\")
        return (self.base_path / safe_key).resolve()

    async def upload(self, key: str, file: BinaryIO) -> None:
        full_path = self._get_full_path(key)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file, f)

    async def download(self, key: str) -> Optional[BinaryIO]:
        full_path = self._get_full_path(key)
        if not full_path.exists() or not full_path.is_file():
            return None
        try:
            return open(full_path, "rb")
        except (OSError, IOError):
            return None

    async def delete(self, key: str) -> bool:
        full_path = self._get_full_path(key)
        try:
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except (OSError, IOError):
            return False

    async def exists(self, key: str) -> bool:
        full_path = self._get_full_path(key)
        return full_path.exists() and full_path.is_file()

    async def get_file_path(self, key: str) -> Optional[str]:
        full_path = self._get_full_path(key)
        if full_path.exists() and full_path.is_file():
            return str(full_path)
        return None


def get_storage_service() -> StorageService:
    from app.core.config import settings
    if settings.STORAGE_BACKEND == "local":
        return LocalStorageService(settings.LOCAL_STORAGE_PATH)
    raise ValueError(f"Unknown storage backend: {settings.STORAGE_BACKEND}")