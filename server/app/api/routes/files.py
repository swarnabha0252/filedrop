import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services.file_service import FileService, FileValidationError, FileSizeError, FileTypeError
from app.core.security import verify_password
from app.schemas.file import (
    FileUploadRequest,
    FileUploadResponse,
    FileMetadataResponse,
    FileDownloadVerifyRequest,
    FileDownloadVerifyResponse,
    FileDeleteRequest,
    ErrorResponse,
    ErrorDetail,
)
from app.core.config import settings

router = APIRouter(prefix="/api/v1/files", tags=["files"])


def get_file_service() -> FileService:
    return FileService()


def get_frontend_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


@router.post("", response_model=FileUploadResponse, status_code=201)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    expiry: int = Form(...),
    password: Optional[str] = Form(None),
    download_limit: Optional[int] = Form(None),
    session: AsyncSession = Depends(get_session),
    file_service: FileService = Depends(get_file_service),
):
    if expiry <= 0:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error=ErrorDetail(code="INVALID_EXPIRY", message="Expiry must be positive")).model_dump(),
        )

    if download_limit is not None and download_limit < 1:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error=ErrorDetail(code="INVALID_DOWNLOAD_LIMIT", message="Download limit must be at least 1")).model_dump(),
        )

    try:
        file_record = await file_service.upload_file(
            session=session,
            file=file.file,
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            expiry_seconds=expiry,
            password=password,
            download_limit=download_limit,
        )
    except FileSizeError as e:
        raise HTTPException(
            status_code=413,
            detail=ErrorResponse(error=ErrorDetail(code="FILE_TOO_LARGE", message=str(e))).model_dump(),
        )
    except FileTypeError as e:
        raise HTTPException(
            status_code=415,
            detail=ErrorResponse(error=ErrorDetail(code="UNSUPPORTED_FILE_TYPE", message=str(e))).model_dump(),
        )
    except FileValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error=ErrorDetail(code="INVALID_FILE", message=str(e))).model_dump(),
        )

    base_url = get_frontend_url(request)
    download_url = f"{base_url}/api/v1/files/{file_record.token}/download"

    return FileUploadResponse(
        token=file_record.token,
        download_url=download_url,
        delete_token=file_record.delete_token,
        expires_at=file_record.expires_at,
        filename=file_record.filename,
        size=file_record.size,
        download_limit=file_record.download_limit,
    )


@router.get("/{token}", response_model=FileMetadataResponse)
async def get_file_metadata(
    token: str,
    session: AsyncSession = Depends(get_session),
    file_service: FileService = Depends(get_file_service),
):
    file_record = await file_service.get_file_by_token(session, token)
    
    if not file_record:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error=ErrorDetail(code="FILE_NOT_FOUND", message="File not found")).model_dump(),
        )

    if file_record.status != "active" or file_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail=ErrorResponse(error=ErrorDetail(code="FILE_EXPIRED", message="This file has expired")).model_dump(),
        )

    return FileMetadataResponse(
        filename=file_record.filename,
        size=file_record.size,
        mime_type=file_record.mime_type,
        expires_at=file_record.expires_at,
        download_count=file_record.download_count,
        download_limit=file_record.download_limit,
        password_required=file_record.password_hash is not None,
    )


@router.post("/{token}/verify", response_model=FileDownloadVerifyResponse)
async def verify_password_for_download(
    token: str,
    request: FileDownloadVerifyRequest,
    session: AsyncSession = Depends(get_session),
    file_service: FileService = Depends(get_file_service),
):
    file_record = await file_service.get_file_by_token(session, token)
    
    if not file_record:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error=ErrorDetail(code="FILE_NOT_FOUND", message="File not found")).model_dump(),
        )

    if file_record.status != "active" or file_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail=ErrorResponse(error=ErrorDetail(code="FILE_EXPIRED", message="This file has expired")).model_dump(),
        )

    if file_record.password_hash is None:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error=ErrorDetail(code="NO_PASSWORD_REQUIRED", message="This file does not require a password")).model_dump(),
        )

    if not verify_password(request.password, file_record.password_hash):
        raise HTTPException(
            status_code=401,
            detail=ErrorResponse(error=ErrorDetail(code="INVALID_PASSWORD", message="Incorrect password")).model_dump(),
        )

    base_url = str(request.__dict__.get("_request", {}).get("base_url", "")).rstrip("/")
    download_url = f"{base_url}/api/v1/files/{token}/download?verified=true"

    return FileDownloadVerifyResponse(authorized=True, download_url=download_url)


@router.get("/{token}/download")
async def download_file(
    token: str,
    verified: bool = False,
    password: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    file_service: FileService = Depends(get_file_service),
):
    file_record = await file_service.get_file_by_token(session, token)
    
    if not file_record:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error=ErrorDetail(code="FILE_NOT_FOUND", message="File not found")).model_dump(),
        )

    if file_record.status != "active" or file_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=410,
            detail=ErrorResponse(error=ErrorDetail(code="FILE_EXPIRED", message="This file has expired")).model_dump(),
        )

    if file_record.download_limit is not None and file_record.download_count >= file_record.download_limit:
        raise HTTPException(
            status_code=410,
            detail=ErrorResponse(error=ErrorDetail(code="DOWNLOAD_LIMIT_REACHED", message="Download limit reached")).model_dump(),
        )

    if file_record.password_hash is not None:
        if not verified and not password:
            raise HTTPException(
                status_code=401,
                detail=ErrorResponse(error=ErrorDetail(code="PASSWORD_REQUIRED", message="Password required")).model_dump(),
            )
        if password and not verify_password(password, file_record.password_hash):
            raise HTTPException(
                status_code=401,
                detail=ErrorResponse(error=ErrorDetail(code="INVALID_PASSWORD", message="Incorrect password")).model_dump(),
            )

    await file_service.increment_download_count(session, file_record)

    file_stream = await file_service.storage.download(file_record.storage_key)
    if not file_stream:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error=ErrorDetail(code="FILE_MISSING", message="File not found in storage")).model_dump(),
        )

    def iter_file():
        try:
            chunk_size = 8192
            while True:
                chunk = file_stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        finally:
            file_stream.close()

    headers = {
        "Content-Disposition": f'attachment; filename="{file_record.filename}"',
        "Content-Type": file_record.mime_type,
        "Content-Length": str(file_record.size),
    }

    return StreamingResponse(iter_file(), headers=headers, media_type=file_record.mime_type)


@router.delete("/{token}")
async def delete_file(
    token: str,
    request: FileDeleteRequest,
    session: AsyncSession = Depends(get_session),
    file_service: FileService = Depends(get_file_service),
):
    success = await file_service.delete_file(session, token, request.delete_token)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error=ErrorDetail(code="FILE_NOT_FOUND", message="File not found or invalid delete token")).model_dump(),
        )

    return {"message": "File deleted successfully"}