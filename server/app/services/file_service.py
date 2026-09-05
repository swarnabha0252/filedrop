import magic
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import BinaryIO, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.file import File, FileStatus
from app.services.storage_service import StorageService, get_storage_service
from app.services.token_service import generate_public_token, generate_private_delete_token
from app.core.security import hash_password, hash_delete_token
from app.core.config import settings


class FileValidationError(Exception):
    pass


class FileSizeError(FileValidationError):
    pass


class FileTypeError(FileValidationError):
    pass


class FileService:
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "text/plain",
        "text/csv",
        "application/json",
        "application/zip",
        "application/x-zip-compressed",
        "application/x-rar-compressed",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }

    def __init__(self, storage: Optional[StorageService] = None):
        self.storage = storage or get_storage_service()

    def _validate_file(self, file: BinaryIO, filename: str, content_type: str) -> tuple[str, int]:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size > settings.max_file_size_bytes:
            raise FileSizeError(f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB")

        if size == 0:
            raise FileValidationError("File is empty")

        detected_type = magic.from_buffer(file.read(8192), mime=True)
        file.seek(0)

        if detected_type not in self.ALLOWED_MIME_TYPES:
            raise FileTypeError(f"File type '{detected_type}' is not allowed")

        safe_filename = self._sanitize_filename(filename)
        return detected_type, size

    def _sanitize_filename(self, filename: str) -> str:
        filename = os.path.basename(filename)
        filename = filename.replace("\\", "").replace("/", "")
        filename = filename.replace("..", "")
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255 - len(ext)] + ext
        return filename or "unnamed"

    def _generate_storage_key(self, token: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1]
        return f"{token}{ext}"

    async def upload_file(
        self,
        session: AsyncSession,
        file: BinaryIO,
        filename: str,
        content_type: str,
        expiry_seconds: int,
        password: Optional[str] = None,
        download_limit: Optional[int] = None,
    ) -> File:
        mime_type, size = self._validate_file(file, filename, content_type)

        for _ in range(5):
            token = generate_public_token()
            delete_token = generate_private_delete_token()
            storage_key = self._generate_storage_key(token, filename)

            password_hash = hash_password(password) if password else None
            delete_token_hash = hash_delete_token(delete_token)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expiry_seconds)

            file_record = File(
                token=token,
                filename=self._sanitize_filename(filename),
                mime_type=mime_type,
                size=size,
                storage_key=storage_key,
                expires_at=expires_at,
                download_limit=download_limit,
                password_hash=password_hash,
                delete_token_hash=delete_token_hash,
            )

            try:
                await self.storage.upload(storage_key, file)
                session.add(file_record)
                await session.commit()
                await session.refresh(file_record)
                file_record.delete_token = delete_token
                return file_record
            except IntegrityError:
                await session.rollback()
                try:
                    await self.storage.delete(storage_key)
                except Exception:
                    pass
                continue
            except Exception:
                await session.rollback()
                try:
                    await self.storage.delete(storage_key)
                except Exception:
                    pass
                raise

        raise FileValidationError("Failed to generate unique token after multiple attempts")

    async def get_file_by_token(self, session: AsyncSession, token: str) -> Optional[File]:
        result = await session.execute(select(File).where(File.token == token))
        return result.scalar_one_or_none()

    async def increment_download_count(self, session: AsyncSession, file: File) -> None:
        file.download_count += 1
        await session.commit()

    async def mark_expired(self, session: AsyncSession, file: File) -> None:
        file.status = FileStatus.EXPIRED
        await session.commit()

    async def mark_deleted(self, session: AsyncSession, file: File) -> None:
        file.status = FileStatus.DELETED
        await session.commit()

    async def delete_file(self, session: AsyncSession, token: str, delete_token: str) -> bool:
        file = await self.get_file_by_token(session, token)
        if not file:
            return False

        from app.core.security import verify_delete_token
        if not verify_delete_token(delete_token, file.delete_token_hash):
            return False

        await self.storage.delete(file.storage_key)
        await self.mark_deleted(session, file)
        return True

    async def cleanup_expired_files(self, session: AsyncSession) -> int:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(File).where(
                File.status == FileStatus.ACTIVE,
                File.expires_at < now,
            )
        )
        expired_files = result.scalars().all()

        count = 0
        for file in expired_files:
            try:
                await self.storage.delete(file.storage_key)
            except Exception:
                pass
            file.status = FileStatus.EXPIRED
            count += 1

        if count > 0:
            await session.commit()
        return count