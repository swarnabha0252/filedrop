import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
async def test_upload_valid_file(client: AsyncClient):
    file_content = b"Hello, World!"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600"}

    response = await client.post("/api/v1/files", files=files, data=data)
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "download_url" in data
    assert "delete_token" in data
    assert "expires_at" in data
    assert data["filename"] == "test.txt"
    assert data["size"] == len(file_content)


@pytest.mark.asyncio
async def test_upload_oversized_file(client: AsyncClient):
    large_content = b"x" * (101 * 1024 * 1024)
    files = {"file": ("large.txt", BytesIO(large_content), "text/plain")}
    data = {"expiry": "3600"}

    response = await client.post("/api/v1/files", files=files, data=data)
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "FILE_TOO_LARGE"


@pytest.mark.asyncio
async def test_upload_invalid_file_type(client: AsyncClient):
    file_content = b"<?php system($_GET['cmd']); ?>"
    files = {"file": ("shell.php", BytesIO(file_content), "application/x-php")}
    data = {"expiry": "3600"}

    response = await client.post("/api/v1/files", files=files, data=data)
    assert response.status_code == 415
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


@pytest.mark.asyncio
async def test_upload_missing_file(client: AsyncClient):
    data = {"expiry": "3600"}

    response = await client.post("/api/v1/files", data=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upload_invalid_expiry(client: AsyncClient):
    file_content = b"test"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "0"}

    response = await client.post("/api/v1/files", files=files, data=data)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_EXPIRY"


@pytest.mark.asyncio
async def test_upload_invalid_download_limit(client: AsyncClient):
    file_content = b"test"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600", "download_limit": "0"}

    response = await client.post("/api/v1/files", files=files, data=data)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_DOWNLOAD_LIMIT"