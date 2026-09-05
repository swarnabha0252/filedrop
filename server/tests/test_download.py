import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
async def test_download_valid_token(client: AsyncClient):
    file_content = b"Download test content"
    files = {"file": ("download.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600"}

    upload_response = await client.post("/api/v1/files", files=files, data=data)
    assert upload_response.status_code == 201
    token = upload_response.json()["token"]

    response = await client.get(f"/api/v1/files/{token}/download")
    assert response.status_code == 200
    assert response.content == file_content
    assert response.headers["content-disposition"] == 'attachment; filename="download.txt"'


@pytest.mark.asyncio
async def test_download_invalid_token(client: AsyncClient):
    response = await client.get("/api/v1/files/invalid_token/download")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "FILE_NOT_FOUND"


@pytest.mark.asyncio
async def test_download_expired_file(client: AsyncClient):
    file_content = b"Expired content"
    files = {"file": ("expired.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "1"}

    upload_response = await client.post("/api/v1/files", files=files, data=data)
    assert upload_response.status_code == 201
    token = upload_response.json()["token"]

    import asyncio
    await asyncio.sleep(2)

    response = await client.get(f"/api/v1/files/{token}/download")
    assert response.status_code == 410
    data = response.json()
    assert data["error"]["code"] == "FILE_EXPIRED"