import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from datetime import datetime
from src.main import app

MOCK_PHOTOS = [
    {
        'Key': 'test_photo1.jpg',
        'LastModified': datetime(2026, 4, 8, 13, 57, 7, 523000),
        'ETag': '"test_etag_1"',
        'Size': 1000000,
        'StorageClass': 'STANDARD',
        'Owner': {
            'DisplayName': 'minio',
            'ID': 'test_owner_id_1'
        }
    },
    {
        'Key': 'test_photo2.png',
        'LastModified': datetime(2026, 4, 8, 13, 57, 7, 468000),
        'ETag': '"test_etag_2"',
        'Size': 500000,
        'StorageClass': 'STANDARD',
        'Owner': {
            'DisplayName': 'minio',
            'ID': 'test_owner_id_2'
        }
    }
]


mock_s3_client = AsyncMock()
mock_s3_client.get_all_objects.return_value = MOCK_PHOTOS

async def override_get_s3_client():
    return mock_s3_client


@pytest.mark.asyncio
async def test_get_all_objects():
    from src.database.s3 import get_s3_client

    app.dependency_overrides[get_s3_client] = override_get_s3_client

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/photo/photos")

        # 2. Проверки
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["Key"] == "test_photo1.jpg"
        mock_s3_client.get_all_objects.assert_awaited_once()

    finally:
        app.dependency_overrides.clear()