from fastapi import APIRouter, status
from app.api.schemas import EventIngest, EventResponse
from app.config import settings
import redis
import json
import uuid

router = APIRouter()
redis_client = redis.Redis.from_url(settings.REDIS_URL)

@router.post("/events", status_code=status.HTTP_202_ACCEPTED, response_model=EventResponse)
async def ingest_event(event: EventIngest):
    event_data = event.model_dump()
    event_id = str(uuid.uuid4())
    event_data["event_id"] = event_id

    # Instant queue push (Memory write)
    redis_client.rpush("raw_events_queue", json.dumps(event_data))

    return EventResponse(status="accepted", event_id=event_id)