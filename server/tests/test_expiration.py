import pytest
import asyncio
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
async def test_expired_file_inaccessible(client: AsyncClient):
    file_content = b"Will expire"
    files = {"file": ("expire.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "1"}

    upload_response = await client.post("/api/v1/files", files=files, data=data)
    assert upload_response.status_code == 201
    token = upload_response.json()["token"]

    await asyncio.sleep(2)

    response = await client.get(f"/api/v1/files/{token}")
    assert response.status_code == 410
    data = response.json()
    assert data["error"]["code"] == "FILE_EXPIRED"


@pytest.mark.asyncio
async def test_cleanup_deletes_expired_object(client: AsyncClient):
    file_content = b"Cleanup test"
    files = {"file": ("cleanup.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "1"}

    upload_response = await client.post("/api/v1/files", files=files, data=data)
    assert upload_response.status_code == 201
    token = upload_response.json()["token"]

    await asyncio.sleep(2)

    from app.services.cleanup_service import cleanup_expired_files
    from app.db.session import async_session_maker
    
    async with async_session_maker() as session:
        count = await cleanup_expired_files(session)
        assert count >= 1

    response = await client.get(f"/api/v1/files/{token}/download")
    assert response.status_code == 410


@pytest.mark.asyncio
async def test_active_file_remains_available(client: AsyncClient):
    file_content = b"Still active"
    files = {"file": ("active.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600"}

    upload_response = await client.post("/api/v1/files", files=files, data=data)
    assert upload_response.status_code == 201
    token = upload_response.json()["token"]

    from app.services.cleanup_service import cleanup_expired_files
    from app.db.session import async_session_maker
    
    async with async_session_maker() as session:
        count = await cleanup_expired_files(session)
        assert count == 0

    response = await client.get(f"/api/v1/files/{token}/download")
    assert response.status_code == 200
    assert response.content == file_content