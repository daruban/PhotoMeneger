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


@pytest.mark.asyncio
async def test_get_all_objects():
    with patch('src.database.s3.s3_photo.get_all_objects', new_callable=AsyncMock) as mock_get_all:
        mock_get_all.return_value = MOCK_PHOTOS

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/photo/photos")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["Key"] == "test_photo1.jpg"
        mock_get_all.assert_awaited_once()