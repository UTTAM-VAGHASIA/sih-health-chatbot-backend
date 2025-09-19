import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_ping():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Backend is running 🚀"}
