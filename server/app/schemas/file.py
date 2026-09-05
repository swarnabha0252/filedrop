from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class FileStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DELETED = "deleted"


class FileUploadRequest(BaseModel):
    expiry: int = Field(..., gt=0, description="Expiration time in seconds")
    password: Optional[str] = Field(None, max_length=128)
    download_limit: Optional[int] = Field(None, ge=1)


class FileUploadResponse(BaseModel):
    token: str
    download_url: HttpUrl
    delete_token: str
    expires_at: datetime
    filename: str
    size: int
    download_limit: Optional[int] = None


class FileMetadataResponse(BaseModel):
    filename: str
    size: int
    mime_type: str
    expires_at: datetime
    download_count: int
    download_limit: Optional[int] = None
    password_required: bool


class FileDownloadVerifyRequest(BaseModel):
    password: str


class FileDownloadVerifyResponse(BaseModel):
    authorized: bool
    download_url: Optional[HttpUrl] = None


class FileDeleteRequest(BaseModel):
    delete_token: str


class ErrorResponse(BaseModel):
    error: "ErrorDetail"


class ErrorDetail(BaseModel):
    code: str
    message: str


class HealthResponse(BaseModel):
    status: str