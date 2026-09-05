import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Enum,
    Index,
    LargeBinary,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class FileStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DELETED = "deleted"


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    download_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delete_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus, values_callable=lambda x: [e.value for e in FileStatus]),
        default=FileStatus.ACTIVE,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_files_expires_at", "expires_at"),
        Index("ix_files_status", "status"),
    )