import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
async def test_path_traversal_filename(client: AsyncClient):
    file_content = b"Traversal test"
    files = {"file": ("../../../etc/passwd", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600"}

    response = await client.post("/api/v1/files", files=files, data=data)
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] != "../../../etc/passwd"
    assert ".." not in data["filename"]


@pytest.mark.asyncio
async def test_malicious_filename(client: AsyncClient):
    file_content = b"Malicious"
    files = {"file": ("file<script>alert(1)</script>.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600"}

    response = await client.post("/api/v1/files", files=files, data=data)
    assert response.status_code == 201
    data = response.json()
    assert "<script>" not in data["filename"]


@pytest.mark.asyncio
async def test_invalid_mime_rejected(client: AsyncClient):
    file_content = b"<?php echo 'hi'; ?>"
    files = {"file": ("test.php", BytesIO(file_content), "application/x-php")}
    data = {"expiry": "3600"}

    response = await client.post("/api/v1/files", files=files, data=data)
    assert response.status_code == 415


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    response = await client.options("/api/v1/files", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    file_content = b"Rate limit test"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    data = {"expiry": "3600"}

    for _ in range(35):
        response = await client.post("/api/v1/files", files=files, data=data)
        if response.status_code == 429:
            break
    else:
        pytest.fail("Rate limiting not triggered")


@pytest.mark.asyncio
async def test_token_unpredictability(client: AsyncClient):
    tokens = set()
    file_content = b"Token test"
    
    for _ in range(100):
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        data = {"expiry": "3600"}
        response = await client.post("/api/v1/files", files=files, data=data)
        assert response.status_code == 201
        tokens.add(response.json()["token"])
    
    assert len(tokens) == 100