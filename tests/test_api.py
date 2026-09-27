import pytest
from httpx import AsyncClient
from app.main import app
import redis
from app.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

@pytest.mark.asyncio
async def test_ingest_event_success():
    payload = {
        "client_id": "test_client_01",
        "event_type": "checkout",
        "latency_ms": 120,
        "user_id": "usr_999"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/events", json=payload)
    
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert "event_id" in data

    raw_event = redis_client.rpop("raw_events_queue")
    assert raw_event is not None


@pytest.mark.asyncio
async def test_ingest_event_invalid_schema():
    invalid_payload = {"event_type": "click"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/events", json=invalid_payload)
    assert response.status_code == 422