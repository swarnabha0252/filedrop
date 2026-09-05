import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
async def test_delete_with_valid_credential(client: AsyncClient):
    file_content = b"Delete me"
    files = {"file": ("delete.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600"}

    upload_response = await client.post("/api/v1/files", files=files, data=data)
    assert upload_response.status_code == 201
    upload_data = upload_response.json()
    token = upload_data["token"]
    delete_token = upload_data["delete_token"]

    response = await client.delete(f"/api/v1/files/{token}", json={"delete_token": delete_token})
    assert response.status_code == 200

    response = await client.get(f"/api/v1/files/{token}/download")
    assert response.status_code == 410


@pytest.mark.asyncio
async def test_delete_with_invalid_credential(client: AsyncClient):
    file_content = b"Cannot delete"
    files = {"file": ("protected.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600"}

    upload_response = await client.post("/api/v1/files", files=files, data=data)
    assert upload_response.status_code == 201
    token = upload_response.json()["token"]

    response = await client.delete(f"/api/v1/files/{token}", json={"delete_token": "invalid_token"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_public_token_cannot_delete(client: AsyncClient):
    file_content = b"Public only"
    files = {"file": ("public.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600"}

    upload_response = await client.post("/api/v1/files", files=files, data=data)
    assert upload_response.status_code == 201
    token = upload_response.json()["token"]

    response = await client.delete(f"/api/v1/files/{token}", json={"delete_token": token})
    assert response.status_code == 404